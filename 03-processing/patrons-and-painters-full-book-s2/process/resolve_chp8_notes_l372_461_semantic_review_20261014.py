from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l372-461"
BACKUP_SUFFIX = ".bak-s2-chp8-notes-l372-461-semantic-review-20261014"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "9e6001bf84f6cea06d730b5810d9807d223adafa9a75c3b0f41595cf95a77b6a",
    "entity-candidates.csv": "5710e3942567deb3189f816ca9ee057a66effa33b18f7c2156d34f90dd07b205",
    "mentions.csv": "60595b379b527c57beef2c0d1012d35d0de72be0a6b7ee3569d3f86ac7731254",
    "s2-coverage.csv": "271fff64d9abffb1a9d4e56266ebf2b14d031829eff765452691fa1848bed1ab",
}

DECISIONS = {
    "st-chp8-p215-dora-coggiola-acknowledgment": (True, "A person-specific research acknowledgment; records the reported assistance without inferring occupation or a fuller institutional name."),
    "st-chp8-p215-pesenti-church-citation": (False, "Secondary bibliographic locator only; no distinct source-to-claim relation is added by this note."),
    "st-chp8-p215-pinetti-document-source-note": (True, "The note explicitly identifies Pinetti's 1916 article as the source of documents in this local discussion while retaining Haskell's authorship of the interpretation."),
    "st-chp8-p217-bottari-citation": (True, "The note identifies published historical letters in two Bottari volumes; the cited pages remain unconsulted."),
    "st-chp8-p218-bottari-citation": (True, "The note identifies published historical letters in Bottari III; the cited pages remain unconsulted."),
    "st-chp8-p219-n1-alternative-subject": (True, "A reported alternative subject identification, attributed to an unconsulted anonymous article; it does not resolve the painting's identity."),
    "st-chp8-p219-n1-citation": (False, "Secondary citation locator; the article itself was not consulted and its author/title are not supplied."),
    "st-chp8-p219-n2-citation": (False, "Secondary citation locator only; the work and cited page remain unidentified and unconsulted."),
    "st-chp8-p220-n1-bottari-citation": (True, "The note points to published historical letters in Bottari III; the cited pages remain unconsulted."),
    "st-chp8-p221-n1-pinetti-citation": (False, "Secondary article citation; the article is not independently consulted here."),
    "st-chp8-p221-n1-s-paolo-painters": (True, "The note directly reports named painters and an unnamed local group working for this specific Bergamo church; the church and painter endpoints are kept source-specific."),
    "st-chp8-p221-n2-moroni-citation": (False, "Bibliographic locator to a secondary biographical dictionary; it does not itself verify Ruffo's career."),
    "st-chp8-p222-n1-manuscript-citation": (False, "This generic citation row duplicates the distinct manuscript-source statement below and adds no separate fact."),
    "st-chp8-p222-n1-manuscript-source": (True, "Haskell explicitly identifies MS 610 as the documentary source of his palace and gallery account."),
    "st-chp8-p222-n2-agnelli-citation": (False, "Citation locator only; the publication relation is separately recorded in the statement about the picture list."),
    "st-chp8-p222-n3-breval-citation": (False, "Bibliographic locator only; the cited page has not been independently read."),
    "st-chp8-p222-n5-luigi-crespi-citation": (False, "Secondary citation locator only; the reported painting location is represented separately."),
    "st-chp8-p222-n5-santangelo-citation": (False, "Catalogue citation locator only; the cited pages have not been independently read."),
    "st-chp8-p222-n5-zanotti-citation": (False, "Secondary citation locator only; the reported painting location is represented separately."),
    "st-chp8-p223-n1-crespi-citation": (False, "Secondary citation locator only; the cited page has not been independently read."),
    "st-chp8-p223-n1-zanotti-citation": (False, "Secondary citation locator only; the cited page has not been independently read."),
    "st-chp8-p223-n3-dominici-citation": (False, "Secondary bibliographic locator; the portrait commission is represented separately."),
    "st-chp8-p223-n3-moroni-citation": (False, "Secondary bibliographic locator; the cited page has not been independently read."),
    "st-chp8-p223-n3-pascoli-citation": (False, "Secondary bibliographic locator; the portrait commission is represented separately."),
    "st-chp8-p223-n4-miller-photos-and-attributions": (True, "Haskell acknowledges two distinct contributions by Dwight Miller: copies of gallery photographs and attribution suggestions; the statement is split by contribution."),
    "st-chp8-p223-n4-orlando-acknowledgement": (True, "Haskell acknowledges Orlando Buonaccorsi for making surviving material about Raimondo available; the material set is not identified, so Raimondo is not used as the supplied object."),
    "st-chp8-p223-n4-ubaldi-family-information": (True, "The note identifies Silvio Ubaldi as a source for some Buonaccorsi-family information, while leaving the publication or document unspecified."),
    "st-chp8-p225-n9-haskell-collection-visit": (True, "The note reports Haskell's visit and his observation that no pictures in the collection could be attributed to Giaquinto; visit and attribution claim are split."),
    "st-chp8-p237-note1-letter-citation": (True, "A specifically identified archival letter in Filza 5904, No. 22, is cited and published in Appendix 4; the original and appendix were not independently consulted."),
    "st-chp8-p237-note2-introduction-letter-citation": (True, "The note identifies a letter of introduction for Crespi and its archive locator; the arrival-with-letter fact and the citation locator are separated."),
    "st-chp8-p237-note3-ecstasy-earlier-work": (True, "The qualified comparison is between two works or work groups, not between the Ecstasy and Crespi as a person; the source-defined painting group receives its own candidate."),
    "st-chp8-p237-note4-luigi-crespi-citation": (False, "Secondary bibliographic locator only; the cited page is not independently read."),
    "st-chp8-p238-note1-march-april-letter-locators": (True, "The note identifies three specific archival letters as sources for the surrounding account; their contents are not assigned individually."),
    "st-chp8-p238-note2-ricci-pepoli-correspondence": (True, "The note explicitly identifies correspondence between Ferdinand and Ricci and letters between Ferdinand and the Pepoli; the two relationships are separated."),
    "st-chp8-p238-note3-ferdinand-letter-draft": (True, "The note concerns one letter from Ferdinand, its original draft in Filza 5904, No. 475, and its publication by Luigi Crespi; archive and publication relations are separated."),
    "st-chp8-p238-note6-return-letter": (True, "The archival letter is explicitly reported as evidence of Crespi's return to Bologna; the letter date is not treated as the travel date."),
    "st-chp8-p239-note1-haskell-eight-month-maximum": (True, "Haskell's maximum-eight-month account is retained as a source-attributed claim and not reconciled with the competing accounts."),
    "st-chp8-p239-note1-luigi-crespi-stay": (True, "Luigi Crespi's reported two-year stay is kept as a conflicting, unverified source claim."),
    "st-chp8-p239-note1-zanotti-multiple-visits": (True, "Haskell's reading of Zanotti as implying several visits is retained as an attributed interpretation."),
    "st-chp8-p239-note2-cross-reference": (False, "Internal cross-reference only; it adds no new claim or independent evidence."),
    "st-chp8-p239-note3-zanotti-and-letter-357": (True, "The specific 28 April 1708 archival letter is separated from the secondary Zanotti citation."),
    "st-chp8-p239-note5-inventory-description": (True, "The note explicitly locates the inventory at Soprintendenza alle Gallerie di Firenze; date range and convenience label are separated as source metadata."),
    "st-chp8-p239-note5-spf-mark": (True, "The inventory's S.P.F. mark is reported for pictures from Ferdinand's own collection, not all Pitti pictures."),
    "st-chp8-p240-exhibition-count-and-loan-sources": (True, "The body passage on p.240 is split into the approximate count, borrowing from Florentine collections, and the absence of loans from the Grand Duke's collection."),
    "st-chp8-p240-note1-fogolari-mehus-acquisition": (False, "Secondary article locator only; the cited source was not independently consulted."),
    "st-chp8-p240-note2-hugford-locator": (False, "Secondary biography locator only; the cited page was not independently consulted."),
    "st-chp8-p240-note3-fogolari-letter12": (True, "A specifically numbered historical letter is cited through Fogolari; its text and original were not independently consulted."),
    "st-chp8-p240-note4-fogolari-letter120": (True, "A specifically dated historical letter is cited through Fogolari; its text and original were not independently consulted."),
    "st-chp8-p240-note5-catalogue-title": (True, "The note identifies the primary 1706 exhibition catalogue for the event; the catalogue itself was not independently consulted."),
    "st-chp8-p241-note1-fogolari-letter116": (True, "The note cites a specific historical letter; the painting's reported Pitti location is split into its own work-location statement."),
    "st-chp8-p241-note2-uncertain-landscape-lender": (True, "The likely link between Ferdinand's two received landscapes and the four lent landscapes remains explicitly probable; the two work groups stay distinct."),
    "st-chp8-p241-note3-1767-catalogue": (True, "The note identifies the introduction to the 1767 exhibition catalogue; people named in its title remain source-level candidates."),
    "st-chp8-p241-note4-sgrilli-locator": (False, "Secondary citation locator only; Sgrilli's cited page was not independently consulted."),
    "st-chp8-p241-note5-gabburri-correspondence": (True, "The note reports Gabburri's correspondence with unnamed Venetian artists; the Bottari publication locator is recorded separately."),
    "st-chp8-p241-note5-gerini-follower": (True, "Haskell identifies Gerini as a significant follower of Ferdinand's contemporary Venetian-art patronage; this remains Haskell's report."),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def by_id(rows: list[dict], key: str) -> dict[str, dict]:
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate {key}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled S2 semantic review of Chapter 8 consolidated notes L372-461.")
    parser.add_argument("--apply", action="store_true", help="Write the reviewed table changes after the dry-run checks pass.")
    args = parser.parse_args()

    paths = {name: TABLES / name for name in EXPECTED_SHA256}
    for name, path in paths.items():
        actual = sha256(path)
        if actual != EXPECTED_SHA256[name]:
            raise SystemExit(f"precondition failed for {name}: expected {EXPECTED_SHA256[name]}, got {actual}")

    statements = read_jsonl(paths["book-statements.jsonl"])
    statement_map = by_id(statements, "statement_id")
    original_quotes = {sid: row["original_quote"] for sid, row in statement_map.items()}
    if set(DECISIONS) != {sid for sid, row in statement_map.items() if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None}:
        actual = {sid for sid, row in statement_map.items() if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None}
        raise SystemExit(f"unset statement set changed: expected {len(DECISIONS)}, found {len(actual)}, missing={sorted(set(DECISIONS)-actual)}, extra={sorted(actual-set(DECISIONS))}")

    candidate_fields, candidates = read_csv(paths["entity-candidates.csv"])
    mention_fields, mentions = read_csv(paths["mentions.csv"])
    coverage_fields, coverage = read_csv(paths["s2-coverage.csv"])
    candidate_map = by_id(candidates, "candidate_id")
    mention_map = by_id(mentions, "mention_id")
    coverage_map = by_id(coverage, "segment_id")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[371:461])
    if len(segment_text) != 14907:
        raise SystemExit(f"source segment length changed: {len(segment_text)}")

    def quote(base_id: str, exact: str) -> str:
        original = original_quotes[base_id]
        if exact not in original:
            raise ValueError(f"quote fragment not found in {base_id}: {exact!r}")
        return exact

    def update(sid: str, *, subject: str | None, predicate: str, object_id: str | None, claim: str,
               note: str | None = None, evidence: str | None = None, mentioned: list[str] | None = None,
               q_updates: dict | None = None, relation_candidate: bool | None = None) -> None:
        row = statement_map[sid]
        row["subject_candidate_id"] = subject
        row["predicate"] = predicate
        row["object_candidate_id"] = object_id
        q = row.setdefault("qualifiers", {})
        q["claim"] = claim
        if relation_candidate is None:
            relation_candidate = DECISIONS[sid][0]
        q["relation_candidate"] = relation_candidate
        q["relation_candidate_note"] = note if note is not None else DECISIONS[sid][1]
        if evidence is not None:
            row["original_quote"] = quote(sid, evidence)
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if q_updates:
            q.update(q_updates)

    new_statements: list[dict] = []

    def add(base_id: str, new_id: str, *, subject: str | None, predicate: str, object_id: str | None,
            claim: str, evidence: str, note: str, mentioned: list[str], q_updates: dict | None = None,
            relation_candidate: bool = True) -> None:
        if new_id in statement_map:
            raise ValueError(f"statement id already exists: {new_id}")
        row = copy.deepcopy(statement_map[base_id])
        row["statement_id"] = new_id
        row["subject_candidate_id"] = subject
        row["predicate"] = predicate
        row["object_candidate_id"] = object_id
        row["original_quote"] = quote(base_id, evidence)
        q = row.setdefault("qualifiers", {})
        q["claim"] = claim
        q["relation_candidate"] = relation_candidate
        q["relation_candidate_note"] = note
        q["mentioned_candidate_ids"] = mentioned
        if q_updates:
            q.update(q_updates)
        new_statements.append(row)
        statement_map[new_id] = row

    # Classify all 55 pre-existing unresolved rows, with semantic corrections to endpoints and claims.
    update("st-chp8-p215-dora-coggiola-acknowledgment", subject=None, predicate="author_research_acknowledgment", object_id="cand-7658",
           claim="Haskell thanks Dora Coggiola of the Biblioteca Civica in Bergamo for her help.")
    update("st-chp8-p215-pesenti-church-citation", subject=None, predicate="footnote_citation", object_id="cand-7655",
           claim="Haskell cites Pesenti for the history of work on Santa Maria Maggiore in Bergamo.")
    update("st-chp8-p215-pinetti-document-source-note", subject="cand-2962", predicate="documents_for_local_discussion_drawn_from", object_id="cand-7657",
           claim="Haskell says the documents discussed here generally come from Angelo Pinetti's 1916 article, while the interpretation is his own though he followed Pinetti closely.")

    update("st-chp8-p217-bottari-citation", subject="cand-2962", predicate="cites_published_letters", object_id="cand-7516",
           claim="Haskell cites letters published by Bottari, volume II, pages 47-56.", evidence="published by Bottari, H, pp. 47-56",
           mentioned=["cand-2962", "cand-3507", "cand-7516"])
    add("st-chp8-p217-bottari-citation", "st-chp8-p217-bottari-volume-iii-citation", subject="cand-2962", predicate="cites_published_letters", object_id="cand-5461",
        claim="Haskell also cites letters published by Bottari, volume III, pages 352-4.", evidence="III, pp. 352-4",
        note="The note identifies published historical letters in Bottari III; the cited pages remain unconsulted.", mentioned=["cand-2962", "cand-3507", "cand-5461"])
    update("st-chp8-p218-bottari-citation", subject="cand-2962", predicate="cites_published_letters", object_id="cand-5461",
           claim="Haskell cites Bottari, volume III, pages 355-6.", evidence="Bottari, HI, pp. 355-6", mentioned=["cand-2962", "cand-3507", "cand-5461"])
    update("st-chp8-p219-n1-alternative-subject", subject="cand-7668", predicate="reported_subject_identification", object_id="cand-7684",
           claim="Haskell reports that an anonymous Bergomum article identifies the represented subject as the Hymn of Liberation after the Crossing.")
    update("st-chp8-p219-n1-citation", subject=None, predicate="footnote_citation", object_id="cand-7689",
           claim="Footnote 1 cites an anonymous article in Bergomum (1947), pages 60-61.")
    update("st-chp8-p219-n2-citation", subject=None, predicate="footnote_citation", object_id="cand-7690",
           claim="Footnote 2 cites Tassi, volume I, page 265.")
    update("st-chp8-p220-n1-bottari-citation", subject="cand-2962", predicate="cites_published_letters", object_id="cand-5461",
           claim="Haskell cites Bottari, volume III, pages 361-369.", evidence="Bonari, III, pp. 361-9", mentioned=["cand-2962", "cand-3507", "cand-5461"],
           q_updates={"qualification": "The page image reads Bottari, volume III, pages 361-9; S0 OCR has Bonari. The cited pages were not independently consulted."})

    # p.221: repair the specific church and artist mappings; atomize the reported painters by endpoint.
    update("st-chp8-p221-n1-pinetti-citation", subject=None, predicate="footnote_citation", object_id="cand-7695",
           claim="Footnote 1 credits Angelo Pinetti's 1920 article, identified in the bibliography as Di alcuni quadri settecenteschi di Bergamo e provincia tornati da Roma in Fiera di Bergamo.")
    update("st-chp8-p221-n1-s-paolo-painters", subject="cand-11462", predicate="worked_for_church_in_bologna", object_id="cand-0871",
           claim="Haskell's note says G. M. Crespi worked for S. Paolo d'Argan in Bologna.", evidence="Among those who worked for it were G. M. Crespi in Bologna",
           mentioned=["cand-11462", "cand-0871", "cand-3398"])
    add("st-chp8-p221-n1-s-paolo-painters", "st-chp8-p221-n1-lazzarini-worked-for-church", subject="cand-11462", predicate="worked_for_church_in_venice", object_id="cand-1374",
        claim="Haskell's note names Gregorio Lazzarini among the painters who worked for S. Paolo d'Argan in Venice.", evidence="Lazzarini, Ricci, Balestra and others in Venice",
        note=DECISIONS["st-chp8-p221-n1-s-paolo-painters"][1], mentioned=["cand-11462", "cand-1374", "cand-3401"])
    add("st-chp8-p221-n1-s-paolo-painters", "st-chp8-p221-n1-ricci-worked-for-church", subject="cand-11462", predicate="worked_for_church_in_venice", object_id="cand-2154",
        claim="Haskell's note names Sebastiano Ricci among the painters who worked for S. Paolo d'Argan in Venice.", evidence="Lazzarini, Ricci, Balestra and others in Venice",
        note=DECISIONS["st-chp8-p221-n1-s-paolo-painters"][1], mentioned=["cand-11462", "cand-2154", "cand-3401"])
    add("st-chp8-p221-n1-s-paolo-painters", "st-chp8-p221-n1-balestra-worked-for-church", subject="cand-11462", predicate="worked_for_church_in_venice", object_id="cand-0168",
        claim="Haskell's note names Antonio Balestra among the painters who worked for S. Paolo d'Argan in Venice.", evidence="Lazzarini, Ricci, Balestra and others in Venice",
        note=DECISIONS["st-chp8-p221-n1-s-paolo-painters"][1], mentioned=["cand-11462", "cand-0168", "cand-3401"])
    add("st-chp8-p221-n1-s-paolo-painters", "st-chp8-p221-n1-local-artists-worked-for-church", subject="cand-11462", predicate="worked_for_church_in_bergamo", object_id="cand-12104",
        claim="Haskell's note says unnamed local Bergamo artists also worked for S. Paolo d'Argan.", evidence="some local artists in Bergamo itself",
        note=DECISIONS["st-chp8-p221-n1-s-paolo-painters"][1], mentioned=["cand-11462", "cand-12104", "cand-6208"])
    update("st-chp8-p221-n2-moroni-citation", subject=None, predicate="footnote_citation", object_id="cand-7696",
           claim="Footnote 2 directs readers to Moroni, volume 69, pages 215-216, for the outline of Ruffo's career.")

    update("st-chp8-p222-n1-manuscript-citation", subject=None, predicate="footnote_citation", object_id="cand-7711",
           claim="Footnote 1 identifies Collezione Antonelli MS 610, described by Girolamo Baruffaldi, as the source of the palace and gallery account.")
    update("st-chp8-p222-n1-manuscript-source", subject="cand-2962", predicate="reports_using_manuscript_as_source", object_id="cand-7711",
           claim="Haskell says his account of the Archbishop's palace is taken from Collezione Antonelli MS 610 in Biblioteca Ariostea, Ferrara.")
    update("st-chp8-p222-n2-agnelli-citation", subject=None, predicate="footnote_citation", object_id="cand-7261",
           claim="Footnote 2 points to J. Agnelli's publication associated in the bibliography with Ruffo's Ferrara gallery.")
    update("st-chp8-p222-n3-breval-citation", subject=None, predicate="footnote_citation", object_id="cand-7713",
           claim="Footnote 3 cites Breval, 1738, volume I, page 193.")
    update("st-chp8-p222-n5-luigi-crespi-citation", subject=None, predicate="footnote_citation", object_id="cand-6591",
           claim="Footnote 5 cites L. Crespi, page 214.")
    update("st-chp8-p222-n5-santangelo-citation", subject=None, predicate="footnote_citation", object_id="cand-7718",
           claim="Footnote 5 also cites Santangelo's Museo di Palazzo Venezia catalogue, pages 2 and 23.")
    update("st-chp8-p222-n5-zanotti-citation", subject=None, predicate="footnote_citation", object_id="cand-7115",
           claim="Footnote 5 cites Zanotti, volume II, page 56.")

    update("st-chp8-p223-n1-crespi-citation", subject=None, predicate="footnote_citation", object_id="cand-6591",
           claim="Footnote 1 also cites L. Crespi, page 259.")
    update("st-chp8-p223-n1-zanotti-citation", subject=None, predicate="footnote_citation", object_id="cand-7115",
           claim="Footnote 1 cites Zanotti, volume II, page 115.")
    update("st-chp8-p223-n3-dominici-citation", subject=None, predicate="footnote_citation", object_id="cand-4835",
           claim="Footnote 3 cites De Dominici, volume IV, page 538.")
    update("st-chp8-p223-n3-moroni-citation", subject=None, predicate="footnote_citation", object_id="cand-7696",
           claim="Footnote 3 also cites Moroni, volume XII, page 71.")
    update("st-chp8-p223-n3-pascoli-citation", subject=None, predicate="footnote_citation", object_id="cand-4552",
           claim="The portrait report cites Pascoli, volume II, page 265.")
    update("st-chp8-p223-n4-miller-photos-and-attributions", subject="cand-7735", predicate="provided_copies_of_gallery_photographs_to_haskell", object_id="cand-7733",
           claim="Haskell thanks Dwight Miller for copies of photographs Miller took of the gallery.", evidence="Mr Dwight Miller for letting me have copies of the photographs he had taken of the gallery",
           mentioned=["cand-7735", "cand-7733"])
    add("st-chp8-p223-n4-miller-photos-and-attributions", "st-chp8-p223-n4-miller-attribution-suggestions", subject="cand-7735", predicate="suggested_attributions_for_gallery_photographs", object_id="cand-7733",
        claim="Haskell thanks Dwight Miller for suggesting many of the attributions for pictures in the gallery.", evidence="Mr Dwight Miller for letting me have copies of the photographs he had taken of the gallery and for suggesting many of the attributions",
        note=DECISIONS["st-chp8-p223-n4-miller-photos-and-attributions"][1], mentioned=["cand-7735", "cand-7733"])
    update("st-chp8-p223-n4-orlando-acknowledgement", subject="cand-0466", predicate="made_surviving_material_about_raimondo_available_to_haskell", object_id=None,
           claim="Haskell thanks Count Orlando Buonaccorsi for making available the little surviving material about his ancestor Raimondo.",
           mentioned=["cand-0466", "cand-0467"])
    update("st-chp8-p223-n4-ubaldi-family-information", subject="cand-7734", predicate="source_for_some_buonaccorsi_family_information", object_id="cand-7729",
           claim="Haskell says some information about the Buonaccorsi family can be found in Silvio Ubaldi; the cited item is not identified.", mentioned=["cand-7734", "cand-7729"])

    update("st-chp8-p225-n9-haskell-collection-visit", subject=None, predicate="author_reports_visit_to_collection", object_id="cand-7765",
           claim="Haskell reports that he visited the Buonaccorsi collection a few years earlier.", evidence="When I visited the collection a few years ago",
           mentioned=["cand-7765"])
    add("st-chp8-p225-n9-haskell-collection-visit", "st-chp8-p225-n9-no-giaquinto-attributions", subject="cand-7765", predicate="no_pictures_attributed_to_artist_reported_after_visit", object_id="cand-1165",
        claim="Haskell reports that none of the pictures in the Buonaccorsi collection could be attributed to Giaquinto.", evidence="none of the pictures there could be attributed to Giaquinto",
        note=DECISIONS["st-chp8-p225-n9-haskell-collection-visit"][1], mentioned=["cand-7765", "cand-1165"])

    update("st-chp8-p237-note1-letter-citation", subject="cand-2962", predicate="cites", object_id="cand-8015",
           claim="Haskell cites a letter dated 26 February 1708 in Archivio Mediceo, Filza 5904, No. 22, published in Appendix 4.", mentioned=["cand-2962", "cand-8015", "cand-0871", "cand-1609"])
    update("st-chp8-p237-note2-introduction-letter-citation", subject="cand-2962", predicate="cites", object_id="cand-8016",
           claim="Haskell cites the letter of introduction for Crespi, Archivio Mediceo, Filza 5897, No. 183, published in Appendix 4.", mentioned=["cand-2962", "cand-8016", "cand-0871"])
    add("st-chp8-p237-note2-introduction-letter-citation", "st-chp8-p237-note2-crespi-arrived-with-letter", subject="cand-0871", predicate="arrived_with_letter_of_introduction", object_id="cand-8016",
        claim="Haskell says Crespi arrived with a letter of introduction, cited as Archivio Mediceo, Filza 5897, No. 183.", evidence="Crespi arrived with a letter of introduction",
        note="The note expressly links Crespi's arrival with a letter of introduction; the sender, recipient and original text are not independently established here.", mentioned=["cand-0871", "cand-8016"])
    update("st-chp8-p237-note3-ecstasy-earlier-work", subject="cand-0877", predicate="described_as_much_earlier_than_painting_group", object_id="cand-12103",
           claim="Haskell says the Ecstasy of St Margaret seems much earlier than the group of Crespi paintings considered in this section.",
           evidence="It seems a much earlier work than the group of paintings by Crespi considered here",
           mentioned=["cand-0877", "cand-12103", "cand-7115", "cand-8022"])
    update("st-chp8-p237-note4-luigi-crespi-citation", subject=None, predicate="footnote_citation", object_id="cand-7578",
           claim="Haskell's note 4 cites L. Crespi, page 211.")

    update("st-chp8-p238-note1-march-april-letter-locators", subject="cand-2962", predicate="cites_archival_letters", object_id="cand-8040",
           claim="Note 1 cites letters from March and April 1708 in Archivio Mediceo, Filza 5904, Nos. 26, 38 and 357.", mentioned=["cand-2962", "cand-8040", "cand-8030", "cand-8031", "cand-8032"])
    update("st-chp8-p238-note2-ricci-pepoli-correspondence", subject="cand-1609", predicate="corresponded_with", object_id="cand-2147",
           claim="The note locates correspondence between Ferdinand and Giovanni Ricci in Archivio Mediceo, Filza 5904, Nos. 167 and 476.", evidence="For the correspondence between Ferdinand and Ricci see Archivio Mediceo, Filza 5904, Nos. 167 anf 476.",
           mentioned=["cand-1609", "cand-2147", "cand-8040", "cand-8033", "cand-8034"],
           q_updates={"qualification": "The cited letters were not independently consulted. S0 OCR reads anf; p.238 image reads and."})
    add("st-chp8-p238-note2-ricci-pepoli-correspondence", "st-chp8-p238-note2-ferdinand-pepoli-correspondence", subject="cand-1609", predicate="corresponded_with", object_id="cand-7377",
        claim="The note locates letters between Ferdinand and the Pepoli in Archivio Mediceo, Filza 5904, Nos. 174, 489 and 490.", evidence="For the letters between Ferdinand and the Pepoli, ibid., Nos. 174, 489 and 490.",
        note=DECISIONS["st-chp8-p238-note2-ricci-pepoli-correspondence"][1], mentioned=["cand-1609", "cand-7377", "cand-8040", "cand-8035", "cand-8036", "cand-8037"])
    update("st-chp8-p238-note3-ferdinand-letter-draft", subject="cand-8038", predicate="original_draft_held_in", object_id="cand-8040",
           claim="The original draft of the letter from Ferdinand cited by Haskell is in Archivio Mediceo, Filza 5904, No. 475.", evidence="The original draft is in the Archivio Mediceo, Filza 5904, No. 475.",
           mentioned=["cand-8038", "cand-8040", "cand-1609"])
    add("st-chp8-p238-note3-ferdinand-letter-draft", "st-chp8-p238-note3-ferdinand-letter-published-by-crespi", subject="cand-8038", predicate="published_in", object_id="cand-6591",
        claim="Haskell refers to the letter from Ferdinand published by Luigi Crespi, page 203.", evidence="See the letter from Ferdinand published by Luigi Crespi, p. 203.",
        note=DECISIONS["st-chp8-p238-note3-ferdinand-letter-draft"][1], mentioned=["cand-8038", "cand-1609", "cand-7716", "cand-6591"])
    update("st-chp8-p238-note6-return-letter", subject="cand-8039", predicate="reports_return_to_bologna", object_id="cand-0871",
           claim="A letter dated 3 November 1709 in Filza 5904 No. 272 is cited as reporting Crespi's return to Bologna.")

    update("st-chp8-p239-note1-haskell-eight-month-maximum", subject=None, predicate="haskell_says_crespi_in_florence_at_most_eight_months_during_1709", object_id="cand-0871",
           claim="Haskell says Crespi was in Florence during 1709 for at most eight months.")
    update("st-chp8-p239-note1-luigi-crespi-stay", subject="cand-7716", predicate="reports_two_year_florence_stay_for", object_id="cand-0871",
           claim="Haskell reports that L. Crespi says Giuseppe Maria Crespi was in Florence for two years.")
    update("st-chp8-p239-note1-zanotti-multiple-visits", subject="cand-7114", predicate="implies_several_florence_visits_by", object_id="cand-0871",
           claim="Haskell says Zanotti, volume II, page 54, implies that Crespi went to Florence several times.")
    update("st-chp8-p239-note2-cross-reference", subject=None, predicate="footnote_cross_reference_to_p237_note1", object_id="cand-8015",
           claim="Note 2 directs the reader to p.237 note 1.", mentioned=["cand-8015"])
    update("st-chp8-p239-note3-zanotti-and-letter-357", subject="cand-1609", predicate="wrote_letter_cited_as_28_april_1708", object_id="cand-8032",
           claim="A letter from Ferdinand dated 28 April 1708 is cited at Archivio Mediceo, Filza 5904, No. 357.", evidence="Letter from Ferdinand of 28 April 1708 in Archivio Medicco, Filza 5904, No. 3 57.",
           mentioned=["cand-1609", "cand-8040", "cand-8032"])
    add("st-chp8-p239-note3-zanotti-and-letter-357", "st-chp8-p239-note3-zanotti-citation", subject=None, predicate="footnote_citation", object_id="cand-7115",
        claim="Note 3 also cites Zanotti, volume II, pages 52 and 54.", evidence="Zanotti, II, pp. 52 and 54",
        note="Secondary citation locator only; the cited pages were not independently read.", mentioned=["cand-7114", "cand-7115"], relation_candidate=False)
    update("st-chp8-p239-note5-inventory-description", subject="cand-8054", predicate="held_at", object_id="cand-8053",
           claim="Haskell says the Pitti apartment inventory is kept at the Soprintendenza alle Gallerie di Firenze; he dates it between 1716 and 1723 and uses 1716 Inventory as a convenience label.",
           evidence="kept at the Soprintendenza alle Gallerie di Firenze")
    add("st-chp8-p239-note5-inventory-description", "st-chp8-p239-note5-inventory-date-and-label", subject="cand-8054", predicate="has_reported_date_range_and_convenience_label", object_id=None,
        claim="Haskell dates the inventory between 1716 and 1723 and says he refers to it as the 1716 Inventory for convenience.",
        evidence="It can be dated between 1716 and 1723. For the sake of convenience I have referred to it as the 1716 Inventory.",
        note="Source metadata rather than an entity-to-entity relation; preserve the date range and do not collapse it to 1716.", mentioned=["cand-8054"], relation_candidate=False)
    update("st-chp8-p239-note5-spf-mark", subject="cand-8054", predicate="marks_ferdinands_own_pictures_with", object_id="cand-8057",
           claim="The note says pictures from Ferdinand's own collection are marked S.P.F. in the inventory.")

    update("st-chp8-p240-exhibition-count-and-loan-sources", subject="cand-7977", predicate="showed_about_250_pictures", object_id="cand-8072",
           claim="Haskell says about 250 pictures were shown at the exhibition.", evidence="250 pictures were shown",
           mentioned=["cand-7977", "cand-8072"], q_updates={"qualification": "The p.240 image reads 'About 250 pictures'; S0 OCR omits About. Original_quote preserves the exact S0 span."})
    add("st-chp8-p240-exhibition-count-and-loan-sources", "st-chp8-p240-pictures-borrowed-from-florence", subject="cand-8072", predicate="borrowed_mostly_from_collections_in", object_id="cand-1041",
        claim="Haskell says nearly all the pictures were borrowed from the great collections of Florence.", evidence="nearly all of them borrowed from the great collections of Florence",
        note=DECISIONS["st-chp8-p240-exhibition-count-and-loan-sources"][1], mentioned=["cand-8072", "cand-1041"])
    add("st-chp8-p240-exhibition-count-and-loan-sources", "st-chp8-p240-no-pictures-from-grand-duke", subject="cand-8072", predicate="none_borrowed_from_collection_of", object_id="cand-8073",
        claim="Haskell says none of the exhibited pictures came from the Grand Duke's collection.", evidence="though none came from the Grand Duke’s",
        note=DECISIONS["st-chp8-p240-exhibition-count-and-loan-sources"][1], mentioned=["cand-8072", "cand-8073"])
    update("st-chp8-p240-note1-fogolari-mehus-acquisition", subject=None, predicate="footnote_citation", object_id="cand-7894",
           claim="Note 1 cites Fogolari, 1937, page 161, note 43, concerning Ricci's acquisition of works by Mehus for Ferdinand.", mentioned=["cand-7894", "cand-2154", "cand-1632", "cand-1609"])
    update("st-chp8-p240-note2-hugford-locator", subject=None, predicate="footnote_citation", object_id="cand-7871",
           claim="Note 2 cites Hugford, page 10, in support of the Gabbiani display passage.")
    update("st-chp8-p240-note3-fogolari-letter12", subject="cand-2962", predicate="cites", object_id="cand-7929",
           claim="Haskell cites Fogolari, 1937, Letter 12 of 7 June 1698.", mentioned=["cand-2962", "cand-7894", "cand-7929"])
    update("st-chp8-p240-note4-fogolari-letter120", subject="cand-2962", predicate="cites", object_id="cand-7950",
           claim="Haskell cites Fogolari, 1937, Letter 120 of 3 September 1707.", mentioned=["cand-2962", "cand-7894", "cand-7950"])
    update("st-chp8-p240-note5-catalogue-title", subject="cand-7977", predicate="catalogued_by", object_id="cand-8069",
           claim="The note identifies the catalogue issued for the 1706 St Luke's Day exhibition and gives its title and Firenze publication line.")

    # The already classified p.240 display row is atomized as part of the same body continuation.
    update("st-chp8-p240-lunette-display", subject="cand-7977", predicate="displayed_pictures_in_groups_of_about_eight_to_ten_in_lunettes_at", object_id="cand-8068",
           claim="Haskell says the pictures were arranged in groups of about eight to ten in the cloister lunettes.", evidence="The pictures were hung in groups of about eight to ten in the lunettes of the cloister.",
           mentioned=["cand-7977", "cand-8068"] , relation_candidate=True,
           note="This printed p.240 body continuation is split into display layout, Ferdinand's loan group and the Grand Prince portrait.")
    add("st-chp8-p240-lunette-display", "st-chp8-p240-twelve-ferdinand-pictures-first-lunette", subject="cand-7977", predicate="displayed_loan_group_in_first_lunette", object_id="cand-8070",
        claim="The first lunette held twelve pictures lent by Ferdinand.", evidence="in the first lunette, he at once came across twelve pictures lent by Ferdinand himself",
        note="The twelve works remain an unidentified group; the statement is printed body text on p.240.", mentioned=["cand-7977", "cand-8070", "cand-1609"])
    add("st-chp8-p240-lunette-display", "st-chp8-p240-grand-prince-portrait-sitter", subject="cand-8071", predicate="portrait_of", object_id="cand-1609",
        claim="The portrait displayed above the chapel door is described as a portrait of the Grand Prince, identified in this passage as Ferdinand.", evidence="a portrait of the Grand Prince",
        note="The sitter is source-identified as the Grand Prince; no portrait title or individual artist is supplied.", mentioned=["cand-8071", "cand-1609"])
    add("st-chp8-p240-lunette-display", "st-chp8-p240-grand-prince-portrait-display-location", subject="cand-8071", predicate="displayed_above_chapel_door_at", object_id="cand-8068",
        claim="Haskell places the Grand Prince portrait above the chapel door in the cloister display.", evidence="above the door of the chapel) by a portrait of the Grand Prince",
        note="The displayed portrait remains an unidentified work candidate; the source gives its position but no title.", mentioned=["cand-8071", "cand-8068"])

    update("st-chp8-p241-note1-fogolari-letter116", subject="cand-2962", predicate="cites", object_id="cand-8099",
           claim="Haskell cites Fogolari, 1937, Letter 116 of 17 October 1705.", evidence="Fogolari, 193 7, Letter 116 of 17 October 1705",
           mentioned=["cand-2962", "cand-7894", "cand-8099"], q_updates={"footnote_marker": 1})
    add("st-chp8-p241-note1-fogolari-letter116", "st-chp8-p241-cagnacci-picture-at-pitti-75", subject="cand-0479", predicate="reported_location_at_pitti_inventory_no_75", object_id="cand-1949",
        claim="Haskell says the Cagnacci picture just discussed is now in the Pitti, number 75.", evidence="The picture is now in the Pitti, No. 75",
        note="The demonstrative refers to Cagnacci's Magdalene in the preceding body text; current location is Haskell's report and is not independently checked.", mentioned=["cand-0479", "cand-1949"], q_updates={"footnote_marker": 1})
    update("st-chp8-p241-note2-uncertain-landscape-lender", subject="cand-1609", predicate="probably_lent_received_landscapes_as_part_of", object_id="cand-8077",
           claim="Haskell says Ferdinand had received two Marco landscapes in May 1706 and that it seems very likely these were among the four lent for the exhibition.")
    update("st-chp8-p241-note3-1767-catalogue", subject="cand-8080", predicate="has_introduction_catalogue", object_id="cand-8081",
           claim="Note 3 refers readers to the introduction to the 1767 exhibition and gives its title, naming Pietro Leopoldo and Maria Luisa di Borbone.")
    update("st-chp8-p241-note4-sgrilli-locator", subject=None, predicate="footnote_citation", object_id="cand-7847",
           claim="Note 4 cites Sgrilli, page 3, for the mid-eighteenth-century praise quoted in the body.")
    update("st-chp8-p241-note5-gabburri-correspondence", subject="cand-1097", predicate="corresponded_with", object_id="cand-8104",
           claim="Haskell says Francesco Gabburri kept in touch with Venetian artists through letters.", evidence="Francesco Gabburri, the connoisssur of drawings, also kept in touch with Venetian artists",
           mentioned=["cand-1097", "cand-8104"], q_updates={"footnote_marker": 5})
    add("st-chp8-p241-note5-gabburri-correspondence", "st-chp8-p241-note5-gabburri-bottari-citation", subject="cand-2962", predicate="cites_published_letters", object_id="cand-7516",
        claim="Haskell points to many letters to Gabburri published by Bottari, volume II.", evidence="many letters to him which are published by Bottari, Vol. II",
        note="The note identifies a published correspondence source; the letters and Bottari volume were not independently consulted.", mentioned=["cand-2962", "cand-1097", "cand-7516"])
    update("st-chp8-p241-note5-gerini-follower", subject="cand-1143", predicate="followed_patronage_of", object_id="cand-1609",
           claim="Haskell identifies Marchese Andrea Gerini as a significant eighteenth-century Florentine follower of Ferdinand's patronage of contemporary Venetian art.",
           q_updates={"footnote_marker": 5})

    # Two new source-local groups required to preserve the stated endpoints at S2.
    new_candidates = [
        {
            "candidate_id": "cand-12103", "index_entry_id": "", "canonical_name": "Group of Giuseppe Maria Crespi paintings discussed by Haskell around p.237",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-defined group compared with the Ecstasy of St Margaret; individual works are not enumerated by this note.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L441",
        },
        {
            "candidate_id": "cand-12104", "index_entry_id": "", "canonical_name": "Unnamed local Bergamo artists reported as working for S. Paolo d'Argan",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-limited group in Pinetti's report; no individual names or number are supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L380",
        },
    ]
    for row in new_candidates:
        if row["candidate_id"] in candidate_map:
            raise ValueError(f"candidate id already exists: {row['candidate_id']}")
        candidates.append(row)
        candidate_map[row["candidate_id"]] = row

    # Correct two note-span mappings and register precise mentions for the new source-local entities and citations.
    mention_map["m-chp8-p221-paolo"]["candidate_id"] = "cand-11462"
    mention_map["m-chp8-p221-paolo"]["note"] = "Specific church/place named in the p.221 note; the generic Churches candidate was an incorrect endpoint."
    mention_map["m-chp8-p221-ricci"]["candidate_id"] = "cand-2154"
    mention_map["m-chp8-p221-ricci"]["note"] = "Sebastiano Ricci person; the earlier work-candidate mapping was incorrect for this painter mention."
    new_mentions = [
        {"mention_id": "m-chp8-p217-bottari-vol2", "segment_id": SEGMENT_ID, "candidate_id": "cand-7516", "surface_form": "published by Bottari, H, pp. 47-56", "start_char": "392", "end_char": "426", "note": "S0 OCR span; the page image reads volume II. Citation candidate for Bottari's published letters."},
        {"mention_id": "m-chp8-p217-bottari-vol3", "segment_id": SEGMENT_ID, "candidate_id": "cand-5461", "surface_form": "III, pp. 352-4", "start_char": "432", "end_char": "446", "note": "Citation to the volume III publication candidate; cited pages were not independently consulted."},
        {"mention_id": "m-chp8-p218-bottari-vol3", "segment_id": SEGMENT_ID, "candidate_id": "cand-5461", "surface_form": "Bottari, HI, pp. 355-6", "start_char": "450", "end_char": "472", "note": "S0 OCR span; the page image reads volume III."},
        {"mention_id": "m-chp8-p220-bottari-vol3", "segment_id": SEGMENT_ID, "candidate_id": "cand-5461", "surface_form": "Bonari, III, pp. 361-9", "start_char": "642", "end_char": "664", "note": "S0 OCR span; the page image reads Bottari, volume III."},
        {"mention_id": "m-chp8-p221-local-artists-group", "segment_id": SEGMENT_ID, "candidate_id": "cand-12104", "surface_form": "some local artists in Bergamo itself", "start_char": "929", "end_char": "965", "note": "Unnamed local painter group explicitly reported as working for S. Paolo d'Argan."},
        {"mention_id": "m-chp8-p237-crespi-painting-group", "segment_id": SEGMENT_ID, "candidate_id": "cand-12103", "surface_form": "group of paintings by Crespi considered here", "start_char": "11504", "end_char": "11548", "note": "Source-defined painting group compared with the Ecstasy; its member works are not enumerated in this note."},
    ]
    for row in new_mentions:
        if row["mention_id"] in mention_map:
            raise ValueError(f"mention id already exists: {row['mention_id']}")
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise ValueError(f"mention span mismatch for {row['mention_id']}: {segment_text[start:end]!r}")
        mentions.append(row)
        mention_map[row["mention_id"]] = row

    # All new and corrected statement endpoints must resolve to candidates.
    candidate_ids = set(candidate_map)
    for row in statements + new_statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for field in ("subject_candidate_id", "object_candidate_id"):
            value = row.get(field)
            if value is not None and value not in candidate_ids:
                raise ValueError(f"unknown endpoint {value} in {row['statement_id']}")
        for candidate_id in (row.get("qualifiers") or {}).get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_ids:
                raise ValueError(f"unknown mentioned candidate {candidate_id} in {row['statement_id']}")

    statement_rows = statements + new_statements
    # Guarantee this segment has no unresolved classification after the planned write.
    unset_after = [row["statement_id"] for row in statement_rows if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None]
    if unset_after:
        raise ValueError(f"unresolved rows remain in segment after plan: {unset_after}")

    coverage_row = coverage_map[SEGMENT_ID]
    coverage_row["note"] = "S2 semantic review of p.215-241 notes is complete. L452 is the verified p.240 body continuation; statements and source links are classified, and the source-local painter group and erroneous church/artist mappings are corrected. P.240 notes are L453-456; p.241 notes are L457-461."

    print(f"segment statements classified: {len(DECISIONS)}")
    print(f"new atomic statements: {len(new_statements)}")
    print(f"new candidates: {len(new_candidates)}")
    print(f"new mentions: {len(new_mentions)}; corrected mention mappings: 2")
    print("segment unresolved after planned write: 0")
    print("source span checks: passed")
    print("candidate endpoint checks: passed")
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    if not args.apply:
        print("No files written. Run with --apply to save backups and apply these exact changes.")
        return 0

    for name, path in paths.items():
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
        shutil.copy2(path, backup)

    write_jsonl(paths["book-statements.jsonl"], statement_rows)
    write_csv(paths["entity-candidates.csv"], candidate_fields, candidates)
    write_csv(paths["mentions.csv"], mention_fields, mentions)
    write_csv(paths["s2-coverage.csv"], coverage_fields, coverage)
    print("APPLIED")
    for name, path in paths.items():
        print(name, sha256(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
