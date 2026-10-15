from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l38-46"
P149_IDS = {
    "st-chp6-p149-aeneid-fresco-dates-footnote",
    "st-chp6-p149-artistic-achievements-identified",
    "st-chp6-p149-baratta-ferrata-financial-difficulties",
    "st-chp6-p149-borromini-dome-s-agnese",
    "st-chp6-p149-borromini-facade-s-agnese",
    "st-chp6-p149-borromini-takes-over-s-agnese-footnote",
    "st-chp6-p149-camillo-character-and-interests",
    "st-chp6-p149-camillo-compared-with-barberini-generosity",
    "st-chp6-p149-camillo-patronage-not-inspiring",
    "st-chp6-p149-camillo-supports-bernini-s-andrea",
    "st-chp6-p149-camillo-unsatisfactory-patron",
    "st-chp6-p149-cortona-aeneid-frescoes",
    "st-chp6-p149-economic-climate-not-wholly-personal",
    "st-chp6-p149-expenses-and-papal-prestige",
    "st-chp6-p149-innocent-x-fiscal-steps",
    "st-chp6-p149-italian-economic-collapse",
    "st-chp6-p149-local-fiscal-difficulties",
    "st-chp6-p149-mola-paints-for-valmontone-palace",
    "st-chp6-p149-passeri-money-troubles-quote",
    "st-chp6-p149-preti-replaces-mola-frescoes",
    "st-chp6-p149-rome-resources-and-recovery",
    "st-chp6-p149-rome-trade-transition-partial",
    "st-chp6-p149-study-of-papal-finances",
    "st-chp6-p149-urban-leaves-treasury-indebted",
    "st-chp6-p149-urban-spending-despite-assurances",
}
EXPECTED_HASHES = {
    STATEMENTS: "14b4d2b6829f46cd20d350f3cafa9333ed4f1ba98120e0c34e7ca2a6519fb2bf",
    CANDIDATES: "7b316b6b610246b3f58635e6a122c902fc8a71b2ee5ce361feb87475b9f61dde",
    MENTIONS: "0db26a9146f1d34951f004a5b3c7215a1f93391cfdefa48436960da2c1dbc47e",
    COVERAGE: "7ec472afbb1078a0418a86edb3284426b13ba87aed6f7214dc630498df4b9e34",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p149-semantic-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp6-p149-entities-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp6-p149-semantic-20261013"),
    COVERAGE: COVERAGE.with_name("s2-coverage.csv.bak-s2-chp6-p149-semantic-20261013"),
}
OLD_COVERAGE_NOTE = (
    "按印刷页149迁移L39-46，含正文L39-43、章节分隔符及本页多行脚注1（L44-46）。"
    "关闭p148 L36→本段L39的Roman Baroque续接；L43句末“In Rome itself, where”续接到下一段L49。"
    "页149脚注1已在本段内回链；脚注2-7待L120-157迁移后回链。OCR校勘记过程，不改S0。"
)
NEW_COVERAGE_NOTE = (
    "印刷页149正文、章节分隔符及脚注1（L39-46）现完成S2语义裁决。关闭p148 L36→本段L39的Roman Baroque续接；"
    "L43片段“In Rome itself, where”已接至p150 L49。脚注1的Briganti与Wittkower引证分别回链至日期断言和Borromini接手工程断言；"
    "脚注2-7已回链至正文。印本校勘仅记于statement/mention，不改S0。"
)
FALSE_NOTE = (
    "This is a source-attributed factual, descriptive, historiographical, or evaluative claim; "
    "it does not assert a relation between the represented entities."
)
TRUE_NOTE = "This is an explicit source-attributed relation candidate; it remains an S2 candidate and creates no formal S6 edge."


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), has_bom


def csv_bytes(fields: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if has_bom else b"") + buffer.getvalue().encode("utf-8")


def make_candidate(cid: str, name: str, suggested_type: str, detail: str, line: int) -> dict[str, str]:
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": suggested_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def make_mention(mid: str, cid: str, surface: str, note: str, segment_text: str, occurrence: int = 0) -> dict[str, str]:
    starts = []
    cursor = 0
    while (found := segment_text.find(surface, cursor)) >= 0:
        starts.append(found)
        cursor = found + 1
    if occurrence < 0 or occurrence >= len(starts):
        raise SystemExit(f"mention surface occurrence missing in segment: {mid} / {surface} / {occurrence}")
    start = starts[occurrence]
    return {
        "mention_id": mid,
        "segment_id": SEGMENT,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def make_statement(
    sid: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    quote: str,
    claim: str,
    first: int,
    last: int,
    mentioned: list[str],
    relation: bool,
    relation_note: str,
    qualification: str,
    *,
    text_layer: str = "authorial historical narrative",
    speaker: str = "Haskell",
    extra: dict | None = None,
) -> dict:
    q = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": "149",
        "pdf_physical_page": 4,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
    }
    if extra:
        q.update(deepcopy(extra))
    return {
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def build() -> dict[Path, bytes]:
    original = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(original[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: expected {expected}, got {actual}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("a p.149 recovery backup already exists; refusing to overwrite it")

    source_lines = source_bytes.decode("utf-8").splitlines()
    segment_text = "\n".join(source_lines[37:46])
    if segment_text[24:41] != "Pietro da Cortona":
        raise SystemExit("p.149 mention offset basis changed")

    statement_rows = [json.loads(line) for line in original[STATEMENTS].decode("utf-8").splitlines() if line.strip()]
    by_id: dict[str, dict] = {}
    for row in statement_rows:
        sid = row["statement_id"]
        if sid in by_id:
            raise SystemExit(f"duplicate statement ID: {sid}")
        by_id[sid] = row
    current = {sid for sid, row in by_id.items() if row.get("segment_id") == SEGMENT}
    if current != P149_IDS:
        raise SystemExit(f"p.149 target set changed: found={len(current)}, expected={len(P149_IDS)}")
    for sid in P149_IDS:
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"p.149 statement is already classified: {sid}")
        if row.get("source_file") != SOURCE_FILE or q.get("printed_page") != "149":
            raise SystemExit(f"p.149 statement provenance mismatch: {sid}")

    candidate_fields, candidates, candidates_bom = read_csv(CANDIDATES)
    mention_fields, mentions, mentions_bom = read_csv(MENTIONS)
    coverage_fields, coverage_rows, coverage_bom = read_csv(COVERAGE)
    cids = {r["candidate_id"] for r in candidates}
    mids = {r["mention_id"] for r in mentions}
    new_candidate_rows = [
        make_candidate("cand-11957", "Pietro da Cortona’s Scenes from the Aeneid frescoes in the papal palace gallery", "work", "The fresco group named on p.149. Distinct from the artist index candidate cand-0359; exact individual scenes and present location are not independently established here.", 39),
        make_candidate("cand-11958", "Gallery in the papal palace at Piazza Navona", "place", "Interior space named as the location of Cortona’s Aeneid frescoes; kept distinct from the papal palace building and from paintings in the gallery.", 39),
        make_candidate("cand-11959", "Painters and sculptors in Passeri’s account of opportunities and money disputes with Camillo Pamfili", "", "An unnamed source-defined group in Passeri’s quoted statement. No members, count, or complete roster is supplied.", 40),
        make_candidate("cand-11960", "Francesco Baratta and Ercole Ferrata in the p.149 financial-difficulties account", "", "A source-defined pair of sculptors explicitly named together in the same claim; this group label does not imply further collaboration.", 40),
        make_candidate("cand-11961", "Camillo Pamfili and his unnamed heirs in the p.149 financial-difficulties account", "", "A source-bounded collective endpoint for this passage only. The heirs’ identities and their relation to the heirs mentioned on p.167 remain unresolved.", 40),
        make_candidate("cand-11962", "Other unnamed artists said to have suffered similar financial complications with Pamfili", "", "The source distinguishes these artists from the named Baratta/Ferrata pair; membership and count are unknown.", 40),
        make_candidate("cand-11963", "Unspecified fine artists employed by Camillo Pamfili in distinguished enterprises", "", "The passage gives no names, count, or individual works for this group.", 40),
        make_candidate("cand-11964", "Competition from England, France, and Holland in Haskell’s account of Italian economic collapse", "", "A source-defined collective of the three named competitors; the text does not specify sectors or assign separate causal weights.", 43),
        make_candidate("cand-11965", "Papal court in Haskell’s fiscal account of Innocent X", "institution", "The court is named only as the setting of repeated financial scandals; no particular office, scandal, or membership is identified.", 43),
    ]
    if any(r["candidate_id"] in cids for r in new_candidate_rows):
        raise SystemExit("a planned p.149 candidate ID already exists")

    new_mentions = [
        make_mention("m-chp6-p149-058", "cand-11959", "painters and sculptors", "Unnamed group to whom Passeri says Camillo gave opportunities; the following 'them' refers back to this group.", segment_text),
        make_mention("m-chp6-p149-059", "cand-11959", "them", "Pronoun referring to the painters and sculptors in Passeri’s quotation.", segment_text, occurrence=0),
        make_mention("m-chp6-p149-060", "cand-11960", "Both the sculptors Francesco Baratta and Ercole Ferrata", "Explicitly named pair, kept as a source-defined group for the joint financial-difficulties claim.", segment_text),
        make_mention("m-chp6-p149-061", "cand-11961", "Pamfili and his heirs", "Collective endpoint in the financial-difficulties claim; heirs remain unnamed.", segment_text),
        make_mention("m-chp6-p149-062", "cand-11962", "other artists", "Unnamed artists reported to have suffered similar complications.", segment_text),
        make_mention("m-chp6-p149-063", "cand-11963", "many very fine artists", "Unnamed group employed by Camillo in distinguished enterprises.", segment_text),
        make_mention("m-chp6-p149-064", "cand-11964", "competition from England, France and Holland", "Collective causal phrase; the three country/region mentions remain separately mapped.", segment_text),
        make_mention("m-chp6-p149-065", "cand-11965", "the court itself", "Papal court named as the setting of repeated financial scandals; specific institutional boundaries remain open.", segment_text),
    ]
    if any(r["mention_id"] in mids for r in new_mentions):
        raise SystemExit("a planned p.149 mention ID already exists")

    # The pre-existing index-derived work/person mapping was semantically wrong:
    # cand-0359 is Pietro da Cortona, not the frescoes or the palace gallery.
    mention_by_id = {r["mention_id"]: r for r in mentions}
    for mid in ("m-chp6-p149-002", "m-chp6-p149-003"):
        mention_by_id[mid]["candidate_id"] = "cand-11957"
        mention_by_id[mid]["note"] = "Pietro da Cortona’s Aeneid fresco group; now separated from the artist candidate cand-0359."
    mention_by_id["m-chp6-p149-004"]["candidate_id"] = "cand-11958"
    mention_by_id["m-chp6-p149-004"]["note"] = "Gallery interior within the papal palace at Piazza Navona."
    mention_by_id["m-chp6-p149-045"]["candidate_id"] = "cand-1831"
    mention_by_id["m-chp6-p149-045"]["note"] = "Papal States as a political entity affected by the Italian economic collapse; use the institution candidate."

    quotes = {
        "st-chp6-p149-aeneid-fresco-dates-footnote": (44, 44, "1 Pietro di Cortona’s frescoes'were painted Between 1651 and 1654—see'Brigand,’1962, p. 146."),
        "st-chp6-p149-artistic-achievements-identified": (39, 39, "were created—Pietro da Cortona’s frescoes of Scenes from the Aeneid in the gallery of the papal palace, and Borromini's dome and façade of the adjoining S. Agnese.1"),
        "st-chp6-p149-baratta-ferrata-financial-difficulties": (40, 40, "Both the sculptors Francesco Baratta and Ercole Ferrata were involved in prolonged financial difficulties with Pamfili and his heirs"),
        "st-chp6-p149-borromini-dome-s-agnese": (39, 39, "Borromini's dome"),
        "st-chp6-p149-borromini-facade-s-agnese": (39, 39, "façade of the adjoining S. Agnese"),
        "st-chp6-p149-borromini-takes-over-s-agnese-footnote": (45, 45, "Borromini took over the building of S. Agnese in Piazza Navona from the Rainaldis in 1653"),
        "st-chp6-p149-camillo-character-and-interests": (40, 40, "He was an amiable man, but very lazy and uncultivated and much more interested in riding than any other activity."),
        "st-chp6-p149-camillo-compared-with-barberini-generosity": (40, 40, "Only in his support of Bernini’s S. Andrea al Quirinale, begun after the death of his uncle, did-Prince Pamfili display the enlightened generosity that had marked the rule of the Barberini."),
        "st-chp6-p149-camillo-patronage-not-inspiring": (40, 40, "his patronage was never very inspiring"),
        "st-chp6-p149-camillo-supports-bernini-s-andrea": (40, 40, "Only in his support of Bernini’s S. Andrea al Quirinale"),
        "st-chp6-p149-camillo-unsatisfactory-patron": (40, 40, "neither now nor later did Prince Pamfili prove a satisfactory art patron"),
        "st-chp6-p149-cortona-aeneid-frescoes": (39, 39, "Pietro da Cortona’s frescoes of Scenes from the Aeneid in the gallery of the papal palace"),
        "st-chp6-p149-economic-climate-not-wholly-personal": (41, 41, "The reasons for this, however, were not wholly personal, for from the ’forties onwards the economic climate became ever more menacing..."),
        "st-chp6-p149-expenses-and-papal-prestige": (42, 42, "Yet expenses too were on a huge scale and a pope sensitive to change and anxious to maintain his prestige was bound to try and cut them down."),
        "st-chp6-p149-innocent-x-fiscal-steps": (43, 43, "already under.Innocent X some steps had to be taken"),
        "st-chp6-p149-italian-economic-collapse": (43, 43, "the papal states were more and more affected by the general collapse of the Italian economy"),
        "st-chp6-p149-local-fiscal-difficulties": (43, 43, "a disastrous drought"),
        "st-chp6-p149-mola-paints-for-valmontone-palace": (40, 40, "Pierfrancesco Mola painted frescoes for his palace at Valmontone"),
        "st-chp6-p149-passeri-money-troubles-quote": (40, 40, "he was always having trouble with them over questions of money."),
        "st-chp6-p149-preti-replaces-mola-frescoes": (40, 40, "which were pulled down and replaced by others by Mattia Preti after one such dispute."),
        "st-chp6-p149-rome-resources-and-recovery": (42, 42, "That the basic resources were vast is shown by the repeated recovery and aggrandisement of Rome long after every observer had noted impending disaster."),
        "st-chp6-p149-rome-trade-transition-partial": (43, 43, "In Rome itself, where"),
        "st-chp6-p149-study-of-papal-finances": (42, 42, "The difficulties facing the student of papal finances are as insuperable today as they were in the seventeenth century."),
        "st-chp6-p149-urban-leaves-treasury-indebted": (43, 43, "When he died he left the Treasury hopelessly indebted"),
        "st-chp6-p149-urban-spending-despite-assurances": (43, 43, "Urban VIII had begun his rule with assurances to this effect, but had followed them up with unparalleled expenditure."),
    }
    if set(quotes) != P149_IDS:
        raise SystemExit("p.149 quote map does not cover the exact target set")
    for sid, (first, last, quote) in quotes.items():
        span = " ".join(source_lines[first - 1:last])
        if normalize(quote) not in normalize(span):
            raise SystemExit(f"source quote preflight failed: {sid}")

    decisions = {
        "st-chp6-p149-aeneid-fresco-dates-footnote": (False, FALSE_NOTE),
        "st-chp6-p149-artistic-achievements-identified": (False, FALSE_NOTE + " The page-break sentence lists examples; creator-to-work claims are represented separately."),
        "st-chp6-p149-baratta-ferrata-financial-difficulties": (True, TRUE_NOTE),
        "st-chp6-p149-borromini-dome-s-agnese": (True, TRUE_NOTE),
        "st-chp6-p149-borromini-facade-s-agnese": (True, TRUE_NOTE),
        "st-chp6-p149-borromini-takes-over-s-agnese-footnote": (True, TRUE_NOTE),
        "st-chp6-p149-camillo-character-and-interests": (False, FALSE_NOTE),
        "st-chp6-p149-camillo-compared-with-barberini-generosity": (False, FALSE_NOTE),
        "st-chp6-p149-camillo-patronage-not-inspiring": (False, FALSE_NOTE),
        "st-chp6-p149-camillo-supports-bernini-s-andrea": (True, TRUE_NOTE),
        "st-chp6-p149-camillo-unsatisfactory-patron": (False, FALSE_NOTE),
        "st-chp6-p149-cortona-aeneid-frescoes": (True, TRUE_NOTE),
        "st-chp6-p149-economic-climate-not-wholly-personal": (False, FALSE_NOTE),
        "st-chp6-p149-expenses-and-papal-prestige": (False, FALSE_NOTE),
        "st-chp6-p149-innocent-x-fiscal-steps": (False, FALSE_NOTE + " The source says measures had to be taken under Innocent X; it does not name the actor who took them."),
        "st-chp6-p149-italian-economic-collapse": (True, TRUE_NOTE),
        "st-chp6-p149-local-fiscal-difficulties": (False, FALSE_NOTE),
        "st-chp6-p149-mola-paints-for-valmontone-palace": (True, TRUE_NOTE),
        "st-chp6-p149-passeri-money-troubles-quote": (True, TRUE_NOTE + " The anonymous artist group is the antecedent of 'them'."),
        "st-chp6-p149-preti-replaces-mola-frescoes": (True, TRUE_NOTE),
        "st-chp6-p149-rome-resources-and-recovery": (False, FALSE_NOTE),
        "st-chp6-p149-rome-trade-transition-partial": (False, FALSE_NOTE + " This is only the opening fragment of a sentence completed on p.150 L49."),
        "st-chp6-p149-study-of-papal-finances": (False, FALSE_NOTE),
        "st-chp6-p149-urban-leaves-treasury-indebted": (True, TRUE_NOTE),
        "st-chp6-p149-urban-spending-despite-assurances": (False, FALSE_NOTE),
    }

    def update(sid: str, *, subject=None, object_=None, predicate: str, claim: str,
               mentioned: list[str], qualification: str | None = None,
               text_layer: str | None = None, ocr: list[dict] | None = None) -> None:
        row = by_id[sid]
        first, last, quote = quotes[sid]
        row["original_quote"] = quote
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["predicate"] = predicate
        q = row["qualifiers"]
        q["source_line_start"] = first
        q["source_line_end"] = last
        q["claim"] = claim
        q["mentioned_candidate_ids"] = mentioned
        q["relation_candidate"], q["relation_candidate_note"] = decisions[sid]
        if qualification is not None:
            q["qualification"] = qualification
        if text_layer is not None:
            q["text_layer"] = text_layer
        if ocr is not None:
            q["ocr_corrections"] = ocr
        q.pop("footnote_pending", None)
        if q.get("footnote_markers"):
            q["footnote_link_status"] = "linked"
            q["footnote_pending"] = False

    update("st-chp6-p149-aeneid-fresco-dates-footnote", subject="cand-11957", predicate="aeneid-frescoes-dated-1651-1654",
           claim="Haskell's footnote says Pietro da Cortona's Aeneid frescoes were painted between 1651 and 1654.",
           mentioned=["cand-11957", "cand-0342", "cand-4473"],
           qualification="The date is attributed to Haskell's note and its cited source Briganti (1962), p.146; the cited publication has not been independently consulted. OCR differences from the printed page are recorded below.",
           text_layer="authorial footnote claim",
           ocr=[{"source_line": 44, "source_form": "di Cortona", "print_reading": "da Cortona", "locator": "CHP-6.pdf physical page 4 / print p.149"},
                {"source_line": 44, "source_form": "frescoes'were", "print_reading": "frescoes were", "locator": "CHP-6.pdf physical page 4 / print p.149"},
                {"source_line": 44, "source_form": "Between", "print_reading": "between", "locator": "CHP-6.pdf physical page 4 / print p.149"},
                {"source_line": 44, "source_form": "Brigand", "print_reading": "Briganti", "locator": "CHP-6.pdf physical page 4 / print p.149"}])
    update("st-chp6-p149-artistic-achievements-identified", subject="cand-4500", predicate="roman-baroque-achievement-examples-identified",
           claim="Haskell completes the previous page's sentence by identifying Cortona's Aeneid frescoes and Borromini's S. Agnese dome and façade as examples of the Roman Baroque achievements created after Camillo's return.",
           mentioned=["cand-4500", "cand-0342", "cand-11957", "cand-11958", "cand-1824", "cand-0406", "cand-6281", "cand-6282", "cand-0693"],
           qualification="This closes the p.148 partial sentence. 'Most beautiful and familiar' remains Haskell's assessment; creator-to-work claims are recorded separately.")
    update("st-chp6-p149-baratta-ferrata-financial-difficulties", subject="cand-11960", object_="cand-11961",
           predicate="sculptors-have-prolonged-financial-difficulties-with-pamfili-and-heirs",
           claim="Haskell says Francesco Baratta and Ercole Ferrata were involved in prolonged financial difficulties with Camillo Pamfili and his unnamed heirs.",
           mentioned=["cand-11960", "cand-0181", "cand-1022", "cand-11961", "cand-1814", "cand-5328"],
           qualification="The two named sculptors and Camillo with his unnamed heirs are represented as source-defined collective endpoints. The heirs' identities and their possible identity with a later passage's heirs remain unresolved.")
    update("st-chp6-p149-borromini-dome-s-agnese", subject="cand-0406", object_="cand-6281",
           predicate="borromini-creates-dome-of-s-agnese",
           claim="Haskell names Borromini's dome of S. Agnese as one of the Roman Baroque achievements created after Camillo's return.",
           mentioned=["cand-0406", "cand-6281", "cand-0693"],
           qualification="The dome is distinct from the church building and façade; the time frame follows the sentence opened on p.148.")
    update("st-chp6-p149-borromini-facade-s-agnese", subject="cand-0406", object_="cand-6282",
           predicate="borromini-creates-facade-of-s-agnese",
           claim="Haskell names Borromini's façade of S. Agnese as one of the Roman Baroque achievements created after Camillo's return.",
           mentioned=["cand-0406", "cand-6282", "cand-0693"],
           qualification="The façade is distinct from the church building and dome; the time frame follows the sentence opened on p.148.")
    take_over = by_id["st-chp6-p149-borromini-takes-over-s-agnese-footnote"]
    take_over["original_quote"] = quotes[take_over["statement_id"]][2]
    take_over["subject_candidate_id"], take_over["object_candidate_id"] = "cand-0406", "cand-0693"
    take_over["predicate"] = "borromini-takes-over-s-agnese-building-project-from-rainaldis"
    tq = take_over["qualifiers"]
    tq.update({"source_line_start": 45, "source_line_end": 45,
               "claim": "Haskell's footnote says Borromini took over the S. Agnese building project from the Rainaldis in 1653.",
               "mentioned_candidate_ids": ["cand-0406", "cand-0693", "cand-3455", "cand-6286", "cand-4557"],
               "relation_candidate": True, "relation_candidate_note": TRUE_NOTE,
               "qualification": "The note uses an unnamed plural Rainaldi reference. Wittkower (1958), p.141, is cited but has not been independently consulted.",
               "speaker": "Haskell footnote", "text_layer": "authorial footnote claim",
               "footnote_markers": [1], "footnote_link_status": "linked", "footnote_pending": False,
               "footnote_segment": SEGMENT, "footnote_target_line": 45, "footnote_printed_page": "149"})
    tq["ocr_corrections"] = [{"source_line": 45, "source_form": "Rainaldis", "print_reading": "Rainaldis", "locator": "CHP-6.pdf physical page 4 / print p.149; no correction, exact plural retained"}]

    update("st-chp6-p149-camillo-character-and-interests", subject="cand-1814", predicate="camillo-character-assessment",
           claim="Haskell characterizes Camillo as amiable but lazy and uncultivated, with riding as his primary interest.",
           mentioned=["cand-1814"],
           qualification="This is Haskell's characterization, not an independently verified personality finding. Footnote 2's bibliographic pointer is already linked in the consolidated p.149 note segment.")
    update("st-chp6-p149-camillo-compared-with-barberini-generosity", subject="cand-1814", object_="cand-3464",
           predicate="camillo-patronage-compared-with-barberini-generosity",
           claim="Haskell presents Camillo's support of S. Andrea as the sole instance in which he displayed the enlightened generosity associated with Barberini rule.",
           mentioned=["cand-1814", "cand-3464", "cand-0312", "cand-0694", "cand-1819"],
           qualification="This is Haskell's evaluative comparison; the specific support relation is recorded separately. The printed page reads 'did Prince'; S0 OCR has 'did-Prince'.",
           text_layer="authorial interpretation",
           ocr=[{"source_line": 40, "source_form": "did-Prince", "print_reading": "did Prince", "locator": "CHP-6.pdf physical page 4 / print p.149"}])
    update("st-chp6-p149-camillo-patronage-not-inspiring", subject="cand-1814", predicate="camillo-patronage-not-inspiring",
           claim="Haskell concludes that Camillo's patronage was never very inspiring.",
           mentioned=["cand-1814"],
           qualification="This is Haskell's evaluative conclusion. Footnote 6's bibliographic and reported-poem claim is already linked in the consolidated note segment.")
    update("st-chp6-p149-camillo-supports-bernini-s-andrea", subject="cand-1814", object_="cand-0694",
           predicate="camillo-supports-bernini-s-andrea",
           claim="Haskell says Camillo supported Bernini's S. Andrea al Quirinale.",
           mentioned=["cand-1814", "cand-0312", "cand-0694", "cand-1819"],
           qualification="The support is the specific patronage relation in the sentence. Haskell dates the beginning of the S. Andrea project to after Innocent X's death; the broader evaluation is recorded separately.")
    update("st-chp6-p149-camillo-unsatisfactory-patron", subject="cand-1814", predicate="camillo-unsatisfactory-art-patron",
           claim="Haskell judges Prince Camillo Pamfili not to have been a satisfactory art patron, either then or later.",
           mentioned=["cand-1814"],
           qualification="This is Haskell's overall evaluative judgment, not an externally established assessment.")
    update("st-chp6-p149-cortona-aeneid-frescoes", subject="cand-0342", object_="cand-11957",
           predicate="cortona-paints-aeneid-frescoes-in-papal-palace-gallery",
           claim="Haskell identifies Pietro da Cortona as the painter of the Aeneid frescoes in the gallery of the papal palace.",
           mentioned=["cand-0342", "cand-11957", "cand-11958", "cand-1824"],
           qualification="The gallery and fresco group are separated from the artist candidate; note 1 dates the frescoes to 1651–1654.")
    update("st-chp6-p149-economic-climate-not-wholly-personal", subject="cand-6247", object_="cand-1814",
           predicate="economic-climate-partly-explains-camillo-patronage",
           claim="Haskell says the reasons for Camillo's unsatisfactory patronage were not wholly personal and that the economic climate grew more menacing from the 1640s onward.",
           mentioned=["cand-6247", "cand-1814", "cand-3569"],
           qualification="This is Haskell's transition and qualified explanation; it does not make economic conditions the sole cause.",
           text_layer="authorial interpretation",
           ocr=[{"source_line": 41, "source_form": "menacing...", "print_reading": "menacing.", "locator": "CHP-6.pdf physical page 4 / print p.149; OCR ellipsis is absent in print"}])
    update("st-chp6-p149-expenses-and-papal-prestige", subject="cand-6287", predicate="papal-expenses-and-prestige-generalization",
           claim="Haskell says papal expenses were very large and generalizes that a pope concerned with change and prestige would try to reduce them.",
           mentioned=["cand-6287"],
           qualification="This is Haskell's general fiscal characterization; the hypothetical pope is not identified.")
    update("st-chp6-p149-innocent-x-fiscal-steps", subject=None, predicate="fiscal-steps-required-under-innocent-x",
           claim="Haskell says some fiscal steps had to be taken under Innocent X.",
           mentioned=["cand-1819"],
           qualification="The passive wording leaves the actor and the measures unspecified; this does not attribute the action directly to Innocent X.",
           text_layer="authorial historical narrative",
           ocr=[{"source_line": 43, "source_form": "under.Innocent", "print_reading": "under Innocent", "locator": "CHP-6.pdf physical page 4 / print p.149"}])
    update("st-chp6-p149-italian-economic-collapse", subject="cand-1831", object_="cand-6247",
           predicate="papal-states-increasingly-affected-by-italian-economic-collapse",
           claim="Haskell says the Papal States were increasingly affected by the general collapse of the Italian economy.",
           mentioned=["cand-1831", "cand-6247", "cand-6290", "cand-5317", "cand-6084"],
           qualification="The Papal States are mapped as a political entity. The mid-century peak and Haskell's attributed explanation by international competition are recorded separately.",
           text_layer="authorial historical interpretation",
           ocr=[{"source_line": 43, "source_form": "due largely To", "print_reading": "due largely to", "locator": "CHP-6.pdf physical page 4 / print p.149"}])
    update("st-chp6-p149-local-fiscal-difficulties", subject="cand-6291", predicate="disastrous-drought-listed-as-local-fiscal-difficulty",
           claim="Haskell lists an unspecified disastrous drought among the local difficulties in the fiscal account.",
           mentioned=["cand-6291", "cand-4490"],
           qualification="No date or exact location is supplied; the event remains distinct from the second War of Castro and the court scandals.")
    update("st-chp6-p149-mola-paints-for-valmontone-palace", subject="cand-1676", object_="cand-6283",
           predicate="mola-paints-frescoes-for-camillo-palace-at-valmontone",
           claim="Haskell says Pierfrancesco Mola painted frescoes for Camillo's palace at Valmontone.",
           mentioned=["cand-1676", "cand-6283", "cand-6285", "cand-3431", "cand-1814"],
           qualification="The palace and fresco group are not individually titled or dated; footnote 4 is linked in the consolidated p.149 note segment.")
    update("st-chp6-p149-passeri-money-troubles-quote", subject="cand-1814", object_="cand-11959",
           predicate="passeri-reports-camillo-money-disputes-with-painters-and-sculptors",
           claim="Passeri says Camillo was continually having trouble with the painters and sculptors over money.",
           mentioned=["cand-1814", "cand-11959", "cand-1856"],
           qualification="The statement is in Passeri's voice, quoted by Haskell after Camillo's death. The group antecedent is explicit; footnote 3 is already linked in the consolidated note segment.",
           text_layer="nested quotation in authorial narrative")
    update("st-chp6-p149-preti-replaces-mola-frescoes", subject="cand-6283", object_="cand-6284",
           predicate="preti-frescoes-replace-mola-frescoes-after-dispute",
           claim="Haskell says the Mola frescoes were pulled down and replaced by Mattia Preti's frescoes after a dispute.",
           mentioned=["cand-6283", "cand-6284", "cand-2056", "cand-1814"],
           qualification="Neither set of frescoes is individually titled or dated; the source does not characterize the dispute more narrowly than the preceding money difficulties. Footnote 4 is linked.")
    update("st-chp6-p149-rome-resources-and-recovery", subject="cand-4490", predicate="rome-recovery-supports-inference-of-vast-resources",
           claim="Haskell infers that Rome's repeated recovery and aggrandizement after observers noted impending disaster demonstrates vast basic resources.",
           mentioned=["cand-4490"],
           qualification="This is Haskell's inference; the resources are not quantified and the observers are unnamed.")
    update("st-chp6-p149-rome-trade-transition-partial", subject="cand-4490", predicate="rome-local-economy-transition-fragment",
           claim="Haskell opens a more local discussion with the incomplete clause 'In Rome itself, where'.",
           mentioned=["cand-4490"],
           qualification="This is an incomplete p.149 fragment; p.150 L49 completes it with the statement that trade and industry were negligible.",
           text_layer="authorial historical narrative and page-break fragment")
    update("st-chp6-p149-study-of-papal-finances", subject="cand-6287", predicate="historiography-of-papal-finances-difficult",
           claim="Haskell says the difficulties facing students of papal finances were as severe in his own time as in the seventeenth century.",
           mentioned=["cand-6287"],
           qualification="This characterizes the research problem; it does not establish that the obstacles in the two periods were literally identical.")
    update("st-chp6-p149-urban-leaves-treasury-indebted", subject="cand-0209", object_="cand-6288",
           predicate="urban-viii-dies-leaving-treasury-hopelessly-indebted",
           claim="Haskell says Urban VIII died leaving the Papal Treasury hopelessly indebted.",
           mentioned=["cand-0209", "cand-6288"],
           qualification="No debt amount or precise recovery date is supplied; the Treasury's formal institutional identity remains provisional.")
    update("st-chp6-p149-urban-spending-despite-assurances", subject="cand-0209", predicate="urban-viii-spending-followed-restraint-assurances",
           claim="Haskell says Urban VIII began his rule with assurances about cutting expenditure but followed them with unprecedented spending.",
           mentioned=["cand-0209"],
           qualification="The comparative term 'unparalleled' is Haskell's evaluation; the passage gives no spending totals.")

    # The p.149 note has two independent bibliographic pointers.
    briganti = make_statement(
        "st-chp6-p149-n1-cites-briganti-1962-p146", "cand-2962", "cand-4473", "cites",
        "—see'Brigand,’1962, p. 146.", "Haskell's footnote cites Briganti (1962), p.146, for the dates of Cortona's Aeneid frescoes.",
        44, 44, ["cand-2962", "cand-4473", "cand-11957"], True, TRUE_NOTE,
        "Citation locator only; Briganti's cited page and publication have not been independently consulted.",
        text_layer="bibliographic citation locator", speaker="Haskell footnote 1",
        extra={"footnote_marker": 1, "footnote_number": 1, "footnote_segment": SEGMENT,
               "footnote_refs": [{"marker": 1, "segment_id": SEGMENT, "source_line": 44}],
               "related_body_statement_ids": ["st-chp6-p149-aeneid-fresco-dates-footnote"],
               "linked_body_statement_ids": ["st-chp6-p149-aeneid-fresco-dates-footnote"],
               "footnote_link_status": "linked", "footnote_text_pending": False,
               "citation_candidate_id": "cand-4473", "citation_publication_candidate_id": "cand-4473",
               "citation_locator": "Briganti, 1962, p.146",
               "citations": [{"source_candidate_id": "cand-4473", "publication_candidate_id": "cand-4473", "locator": "Briganti, 1962, p.146"}],
               "cited_material_not_independently_consulted": True,
               "relation_candidate_note": "This records the bibliographic path only; it does not independently verify the dates or cited contents."})
    wittkower = make_statement(
        "st-chp6-p149-n1-cites-wittkower-1958-p141", "cand-2962", "cand-4557", "cites",
        "Wittkower, 1958, p. 141.", "Haskell's footnote cites Wittkower (1958), p.141, for Borromini taking over the S. Agnese project in 1653.",
        46, 46, ["cand-2962", "cand-4557", "cand-0406", "cand-0693"], True, TRUE_NOTE,
        "Citation locator only; Wittkower's cited page and publication have not been independently consulted.",
        text_layer="bibliographic citation locator", speaker="Haskell footnote 1",
        extra={"footnote_marker": 1, "footnote_number": 1, "footnote_segment": SEGMENT,
               "footnote_refs": [{"marker": 1, "segment_id": SEGMENT, "source_line": 45}],
               "related_body_statement_ids": ["st-chp6-p149-borromini-takes-over-s-agnese-footnote"],
               "linked_body_statement_ids": ["st-chp6-p149-borromini-takes-over-s-agnese-footnote"],
               "footnote_link_status": "linked", "footnote_text_pending": False,
               "citation_candidate_id": "cand-4557", "citation_publication_candidate_id": "cand-4557",
               "citation_locator": "Wittkower, 1958, p.141",
               "citations": [{"source_candidate_id": "cand-4557", "publication_candidate_id": "cand-4557", "locator": "Wittkower, 1958, p.141"}],
               "cited_material_not_independently_consulted": True,
               "relation_candidate_note": "This records the bibliographic path only; it does not independently verify the takeover date or cited contents."})

    additions = [
        make_statement("st-chp6-p149-passeri-says-camillo-gives-artists-opportunities", "cand-1814", "cand-11959",
                       "passeri-reports-camillo-gives-opportunities-to-artists",
                       "Though he, more than anyone of his time, gave opportunities to painters and sculptors,",
                       "Passeri says Camillo gave opportunities to painters and sculptors more than anyone of his time.",
                       40, 40, ["cand-1814", "cand-11959", "cand-1856"], True, TRUE_NOTE,
                       "This is Passeri's quoted assessment, not an independently established comparative ranking. The group is the same explicit antecedent as 'them' in the following clause.",
                       text_layer="nested quotation in authorial narrative", speaker="Giambattista Passeri, quoted by Haskell",
                       extra={"footnote_markers": [3], "footnote_link_status": "linked", "footnote_pending": False,
                              "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 125,
                              "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l125-p149-n3"]}),
        make_statement("st-chp6-p149-camillo-mean", "cand-1814", None, "camillo-described-as-mean",
                       "Above all he was mean.", "Haskell describes Camillo as mean.",
                       40, 40, ["cand-1814"], False, FALSE_NOTE,
                       "This is Haskell's attributed character judgment; footnote 2 points to Barozzi e Berchet, which has not been independently examined.",
                       text_layer="authorial evaluative narrative",
                       extra={"footnote_markers": [2], "footnote_link_status": "linked", "footnote_pending": False,
                              "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 124,
                              "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l124-p149-n2"]}),
        make_statement("st-chp6-p149-other-artists-suffer-similar-financial-complications", "cand-11962", "cand-11961",
                       "other-artists-suffer-similar-financial-complications-with-pamfili-and-heirs",
                       "and other artists also suffered complications of the same kind.",
                       "Haskell says other unnamed artists experienced financial complications of the same kind with Camillo Pamfili and his heirs.",
                       40, 40, ["cand-11962", "cand-11961", "cand-1814", "cand-5328"], True, TRUE_NOTE,
                       "The group membership and count are unknown. 'Of the same kind' refers to the financial difficulties in the preceding clause; footnote 5 is linked in the consolidated note segment.",
                       extra={"footnote_markers": [5], "footnote_link_status": "linked", "footnote_pending": False,
                              "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 127,
                              "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l127-p149-n5"]}),
        make_statement("st-chp6-p149-camillo-employs-fine-artists", "cand-1814", "cand-11963",
                       "camillo-employs-fine-artists-in-distinguished-enterprises",
                       "many very fine artists were employed by him in enterprises of the greatest distinction",
                       "Haskell says many fine artists were employed by Camillo in enterprises he calls highly distinguished.",
                       40, 40, ["cand-1814", "cand-11963"], True, TRUE_NOTE,
                       "The artists, number, and individual enterprises are not named; Haskell's praise is retained as his wording.",
                       extra={"footnote_markers": [6], "footnote_link_status": "linked", "footnote_pending": False,
                              "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 128,
                              "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l128-p149-n6"]}),
        make_statement("st-chp6-p149-two-generations-to-understand-financial-situation", None, None,
                       "financial-situation-takes-two-generations-to-become-clear",
                       "It took about two generations for the situation to become clear to everybody",
                       "Haskell says it took about two generations for the financial situation to become clear to everyone.",
                       43, 43, ["cand-6288", "cand-1819"], False, FALSE_NOTE,
                       "The approximate duration and the referent of 'everybody' remain as stated by Haskell; no exact start or end date is given."),
        make_statement("st-chp6-p149-treasury-never-fully-recovers", "cand-6288", None,
                       "papal-treasury-never-fully-recovers",
                       "and it never fully recovered.",
                       "Haskell says the Papal Treasury never fully recovered after the debt left at Urban VIII's death.",
                       43, 43, ["cand-6288", "cand-0209"], False, FALSE_NOTE,
                       "The pronoun refers to the Treasury. The source gives no recovery measure or date."),
        make_statement("st-chp6-p149-innocent-fiscal-measures-fitful-inadequate", "cand-1819", "cand-4490",
                       "fiscal-steps-fitful-and-inadequate-for-rome",
                       "As always they were only fitful and did nothing to remedy the real troubles facing Rome. Indeed this was hardly possible.",
                       "Haskell says the fiscal steps were fitful and did not remedy Rome's real difficulties, which he considered difficult to remedy.",
                       43, 43, ["cand-1819", "cand-4490"], False, FALSE_NOTE,
                       "This is Haskell's evaluation of unspecified measures, not a claim that Innocent X personally carried them out."),
        make_statement("st-chp6-p149-second-war-costly-victorious", "cand-6289", None,
                       "second-war-of-castro-costly-but-victorious",
                       "the expensive, though victorious, second War of Castro",
                       "Haskell characterizes the second War of Castro as costly but victorious.",
                       43, 43, ["cand-6289"], False, FALSE_NOTE,
                       "Kept distinct from the first War of Castro treated earlier in the chapter; no dates are supplied here."),
        make_statement("st-chp6-p149-repeated-papal-court-financial-scandals", "cand-11965", None,
                       "repeated-financial-scandals-at-papal-court",
                       "repeated financial scandals in the court itself",
                       "Haskell lists repeated financial scandals at the papal court among local fiscal difficulties.",
                       43, 43, ["cand-11965", "cand-1819"], False, FALSE_NOTE,
                       "The passage does not identify individual scandals or specify the institutional boundaries of 'the court'."),
        make_statement("st-chp6-p149-economy-collapse-climaxes-mid-century", "cand-6247", None,
                       "italian-economic-collapse-reaches-mid-century-climax",
                       "which reached its climax in the middle of the century",
                       "Haskell says the general collapse of the Italian economy reached its climax in the middle of the seventeenth century.",
                       43, 43, ["cand-6247"], False, FALSE_NOTE,
                       "This is Haskell's periodization; no exact year is given."),
        make_statement("st-chp6-p149-collapse-linked-to-country-competition", "cand-6247", "cand-11964",
                       "italian-economic-collapse-attributed-largely-to-country-competition",
                       "due largely To competition from England, France and Holland.",
                       "Haskell attributes much of the Italian economic collapse to competition from England, France, and Holland.",
                       43, 43, ["cand-6247", "cand-11964", "cand-6290", "cand-5317", "cand-6084"], True, TRUE_NOTE,
                       "This preserves Haskell's causal attribution and its 'largely' qualifier; the passage does not specify sectors or separate causal weights.",
                       text_layer="authorial historical interpretation",
                       extra={"ocr_corrections": [{"source_line": 43, "source_form": "due largely To", "print_reading": "due largely to", "locator": "CHP-6.pdf physical page 4 / print p.149"}]}),
    ]
    # There are eleven non-citation additions above; the exact total is checked below.
    additions.extend([briganti, wittkower])
    if len(additions) != 13:
        raise SystemExit("unexpected p.149 addition count")
    if set(by_id) & {r["statement_id"] for r in additions}:
        raise SystemExit("planned p.149 statement ID already exists")

    # Link the two note citations from the body and preserve p.148/p.150 continuations.
    by_id["st-chp6-p149-aeneid-fresco-dates-footnote"]["qualifiers"].update({
        "footnote_markers": [1], "footnote_link_status": "linked", "footnote_pending": False,
        "footnote_segment": SEGMENT, "footnote_target_line": 44, "footnote_printed_page": "149",
        "footnote_citation_statement_ids": [briganti["statement_id"]],
    })
    take_over["qualifiers"]["footnote_citation_statement_ids"] = [wittkower["statement_id"]]
    by_id["st-chp6-p149-camillo-character-and-interests"]["qualifiers"].update({
        "footnote_citation_statement_ids": ["st-chp6-notes-l124-p149-n2"],
    })
    by_id["st-chp6-p149-passeri-money-troubles-quote"]["qualifiers"]["footnote_citation_statement_ids"] = ["st-chp6-notes-l125-p149-n3"]
    by_id["st-chp6-p149-mola-paints-for-valmontone-palace"]["qualifiers"].update({
        "footnote_markers": [4], "footnote_link_status": "linked", "footnote_pending": False,
        "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 126,
        "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l126-p149-n4"],
    })
    by_id["st-chp6-p149-preti-replaces-mola-frescoes"]["qualifiers"].update({
        "footnote_markers": [4], "footnote_link_status": "linked", "footnote_pending": False,
        "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 126,
        "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l126-p149-n4"],
    })
    by_id["st-chp6-p149-baratta-ferrata-financial-difficulties"]["qualifiers"].update({
        "footnote_markers": [5], "footnote_link_status": "linked", "footnote_pending": False,
        "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 127,
        "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l127-p149-n5"],
    })
    by_id["st-chp6-p149-camillo-patronage-not-inspiring"]["qualifiers"].update({
        "footnote_markers": [6], "footnote_link_status": "linked", "footnote_pending": False,
        "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 128,
        "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l128-p149-n6"],
    })
    by_id["st-chp6-p149-italian-economic-collapse"]["qualifiers"].update({
        "footnote_markers": [7], "footnote_link_status": "linked", "footnote_pending": False,
        "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157", "footnote_target_line": 129,
        "footnote_printed_page": "149", "footnote_citation_statement_ids": ["st-chp6-notes-l129-p149-n7"],
    })

    new_ids = {r["statement_id"] for r in additions}
    for row in additions:
        if row["source_file"] != SOURCE_FILE or row["segment_id"] != SEGMENT:
            raise SystemExit(f"new statement provenance mismatch: {row['statement_id']}")
        if normalize(row["original_quote"]) not in normalize(" ".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]])):
            raise SystemExit(f"new statement quote does not match source: {row['statement_id']}")
    all_candidate_ids = cids | {r["candidate_id"] for r in new_candidate_rows}
    for row in additions:
        for key in ("subject_candidate_id", "object_candidate_id"):
            value = row.get(key)
            if value and value not in all_candidate_ids:
                raise SystemExit(f"new statement has missing {key}: {row['statement_id']} -> {value}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in all_candidate_ids:
                raise SystemExit(f"new statement mention candidate missing: {row['statement_id']} -> {cid}")

    # Remap existing page rows and insert new rows adjacent to their source claims.
    insert_after = {
        "st-chp6-p149-aeneid-fresco-dates-footnote": [briganti],
        "st-chp6-p149-borromini-takes-over-s-agnese-footnote": [wittkower],
        "st-chp6-p149-camillo-character-and-interests": [next(r for r in additions if r["statement_id"].endswith("-camillo-mean"))],
        "st-chp6-p149-passeri-money-troubles-quote": [next(r for r in additions if r["statement_id"].endswith("-artists-opportunities"))],
        "st-chp6-p149-baratta-ferrata-financial-difficulties": [next(r for r in additions if r["statement_id"].endswith("-similar-financial-complications"))],
        "st-chp6-p149-camillo-patronage-not-inspiring": [next(r for r in additions if r["statement_id"].endswith("-employs-fine-artists"))],
        "st-chp6-p149-urban-leaves-treasury-indebted": [next(r for r in additions if r["statement_id"].endswith("-never-fully-recovers")),
                                                            next(r for r in additions if r["statement_id"].endswith("-two-generations-to-understand-financial-situation"))],
        "st-chp6-p149-innocent-x-fiscal-steps": [next(r for r in additions if r["statement_id"].endswith("-fitful-inadequate"))],
        "st-chp6-p149-local-fiscal-difficulties": [next(r for r in additions if r["statement_id"].endswith("-costly-victorious")),
                                                    next(r for r in additions if r["statement_id"].endswith("-financial-scandals"))],
        "st-chp6-p149-italian-economic-collapse": [next(r for r in additions if r["statement_id"].endswith("-climaxes-mid-century")),
                                                    next(r for r in additions if r["statement_id"].endswith("-country-competition"))],
    }
    additions_in_table: list[dict] = []
    out_statements: list[dict] = []
    for row in statement_rows:
        out_statements.append(row)
        additions_in_table.extend(insert_after.get(row["statement_id"], []))
        out_statements.extend(insert_after.get(row["statement_id"], []))
    for row in additions:
        if row["statement_id"] not in {x["statement_id"] for x in additions_in_table}:
            out_statements.append(row)
    if {r["statement_id"] for r in out_statements} != set(by_id) | new_ids:
        raise SystemExit("statement rewrite lost or duplicated rows")

    # Link newly created citation statement rows to their own concise body claims.
    out_by_id = {r["statement_id"]: r for r in out_statements}
    # Update coverage once: its previous complete flag did not reflect 25 unset statements.
    seen_coverage = 0
    for row in coverage_rows:
        if row.get("segment_id") == SEGMENT:
            seen_coverage += 1
            if row.get("note") != OLD_COVERAGE_NOTE:
                raise SystemExit("p.149 coverage note preflight failed")
            row["note"] = NEW_COVERAGE_NOTE
    if seen_coverage != 1:
        raise SystemExit(f"expected one p.149 coverage row, found {seen_coverage}")

    candidate_rows = candidates + new_candidate_rows
    mention_rows = mentions + new_mentions
    if len({r["candidate_id"] for r in candidate_rows}) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs after p.149 preparation")
    if len({r["mention_id"] for r in mention_rows}) != len(mention_rows):
        raise SystemExit("duplicate mention IDs after p.149 preparation")
    p149_after = [r for r in out_statements if r.get("segment_id") == SEGMENT]
    if len(p149_after) != len(P149_IDS) + len(additions) or any(r["qualifiers"].get("relation_candidate") not in (True, False) for r in p149_after):
        raise SystemExit("p.149 classification or addition count preflight failed")
    for row in new_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"new mention span failed: {row['mention_id']}")
    for mid in ("m-chp6-p149-002", "m-chp6-p149-003", "m-chp6-p149-004"):
        row = next(r for r in mention_rows if r["mention_id"] == mid)
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"existing mention span failed: {mid}")

    new_files = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in out_statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(candidate_fields, candidate_rows, candidates_bom),
        MENTIONS: csv_bytes(mention_fields, mention_rows, mentions_bom),
        COVERAGE: csv_bytes(coverage_fields, coverage_rows, coverage_bom),
    }
    return new_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve p.149 of CHP-6 at S2.")
    parser.add_argument("--apply", action="store_true", help="write only after all guarded checks pass")
    args = parser.parse_args()
    outputs = build()
    print("p.149 semantic preflight: PASS")
    print("planned additions: 13 statements, 9 candidates, 8 mentions")
    print("p.149 target: 25 existing statements classified; final segment total 38")
    if not args.apply:
        print("dry-run only; no files written")
        return
    for path, expected in EXPECTED_HASHES.items():
        if sha256(path.read_bytes()) != expected:
            raise SystemExit(f"input changed after preflight: {path.relative_to(ROOT)}")
    for original, backup in BACKUPS.items():
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")
        shutil.copy2(original, backup)
    temp_paths: dict[Path, Path] = {}
    try:
        for target, data in outputs.items():
            fd, name = tempfile.mkstemp(prefix=f".{target.stem}.p149-", dir=target.parent)
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            temp_paths[target] = Path(name)
        for target, temp in temp_paths.items():
            os.replace(temp, target)
    finally:
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
    print("p.149 protected apply: PASS")
    for path in outputs:
        print(f"{path.relative_to(ROOT)} sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
