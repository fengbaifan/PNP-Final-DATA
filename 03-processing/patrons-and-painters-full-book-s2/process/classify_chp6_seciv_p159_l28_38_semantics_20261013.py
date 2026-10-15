from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
SEGMENT = "chp-6:06_CHP-6_sec_iv:l28-38"
BACKUP = ".bak-s2-chp6-seciv-p159-l28-38-semantics-20261013"

EXPECTED = {
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    STATEMENTS: "173888c63465c761027b46c75059a7ab58a570b561c72fdd84d71660e7e82c1d",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "1a4854217cd821631b52f976a88f81c2bcb983f7f886dfb16bcbc6bbf211266d",
    COVERAGE: "b0aee385f09554633aaa3402fadee412e12746ab7b1df03407dbe863d1c3f55c",
}

TARGETS = {
    "st-chp6-p159-algardi-bernini-treatment",
    "st-chp6-p159-attacks-raphael-critics",
    "st-chp6-p159-bellori-breaks-tradition",
    "st-chp6-p159-bellori-caravaggio",
    "st-chp6-p159-bellori-consistent-view",
    "st-chp6-p159-bellori-critical-priority",
    "st-chp6-p159-bellori-descrizione",
    "st-chp6-p159-bellori-ideal-criterion",
    "st-chp6-p159-bellori-influence",
    "st-chp6-p159-bellori-lives-1672-preface",
    "st-chp6-p159-bellori-portrait",
    "st-chp6-p159-bellori-selectivity",
    "st-chp6-p159-carracci-rescue",
    "st-chp6-p159-carracci-return-to-models",
    "st-chp6-p159-chiari-advice",
    "st-chp6-p159-classical-qualities",
    "st-chp6-p159-cortona-ignored",
    "st-chp6-p159-domenichino-hero",
    "st-chp6-p159-extremes-dangerous",
    "st-chp6-p159-mannerism-decline",
    "st-chp6-p159-maratta-appeal-pupil",
    "st-chp6-p159-maratta-commission",
    "st-chp6-p159-maratta-reputation",
    "st-chp6-p159-poussin-friend-influence",
    "st-chp6-p159-prepares-neoclassicism-partial",
    "st-chp6-p159-raphael-devotion",
    "st-chp6-p159-sacchi-unpublished-life",
}

TRUE_NOTES = {
    "st-chp6-p159-algardi-bernini-treatment": "This records the Lives' coverage of Algardi; Bernini's separate coverage is split into its own statement.",
    "st-chp6-p159-attacks-raphael-critics": "Haskell reports Bellori attacking unnamed opponents of the Raphael cult. The target group remains open; the embedded criticism is attributed to those opponents, not to Haskell or Bellori.",
    "st-chp6-p159-bellori-breaks-tradition": "This records Bellori's stated break with the art-historical tradition attributed to Vasari and Baglione; 'feebly' is Haskell's evaluation.",
    "st-chp6-p159-bellori-caravaggio": "Haskell contrasts the Lives' treatment of Caravaggio with Bellori's reported respect for him; preserve both sides of the source claim.",
    "st-chp6-p159-bellori-descrizione": "This records Bellori's authorship of the Descrizione; the work's relationship to Raphael devotion is stated separately.",
    "st-chp6-p159-bellori-ideal-criterion": "Haskell connects Bellori's criterion to the Ideal concept; the separate Agucchi-to-Ideal relation is recorded independently.",
    "st-chp6-p159-bellori-lives-1672-preface": "This records Haskell's statement that Bellori published the Lives in 1672; the book's inclusion of the earlier lecture as preface is separate.",
    "st-chp6-p159-bellori-portrait": "Haskell reports a later portrait of Bellori painted by Maratta; date, title, version and location remain unspecified.",
    "st-chp6-p159-bellori-selectivity": "This records Haskell's account of the Lives' non-exhaustive selection of artists, lives and works.",
    "st-chp6-p159-carracci-rescue": "Haskell credits Annibale Carracci with the rescue; the Bolognese followers are linked in a separate statement.",
    "st-chp6-p159-carracci-return-to-models": "This records the Bolognese followers' return to nature; study of antiquity and the great masters is split out.",
    "st-chp6-p159-chiari-advice": "This records Maratta's consultation with Bellori; Chiari's separate consultation is recorded independently, preserving Haskell's uncertainty about advice beyond iconography.",
    "st-chp6-p159-classical-qualities": "This records Bellori singling out classical qualities in contemporaries and predecessors for praise; it remains Haskell's account.",
    "st-chp6-p159-cortona-ignored": "This is a source-grounded negative claim about Cortona's absence from Bellori's Lives, not a general claim about Bellori's knowledge of him.",
    "st-chp6-p159-domenichino-hero": "Haskell presents Domenichino as one of Bellori's heroes and recalls the earlier teacher-student relationship also stated on p. 158.",
    "st-chp6-p159-extremes-dangerous": "This records Haskell's explicit comparison of naturalism and mannerism as artistic tendencies; it is not an independently verified aesthetic judgment.",
    "st-chp6-p159-mannerism-decline": "This preserves Haskell's historiographical claim about post-Renaissance art and mannerism as a source-attributed concept relation.",
    "st-chp6-p159-maratta-appeal-pupil": "This records Maratta's pupil relationship to Sacchi; Maratta's appeal to Bellori is a separate statement.",
    "st-chp6-p159-maratta-commission": "This records Bellori's reported help obtaining an early commission for Maratta in 1652; the commission and work remain unidentified.",
    "st-chp6-p159-maratta-reputation": "This records Bellori's efforts, as reported by Haskell, to promote Maratta's reputation.",
    "st-chp6-p159-poussin-friend-influence": "This records Haskell's description of Poussin as Bellori's great friend; influence on the book is split separately.",
    "st-chp6-p159-prepares-neoclassicism-partial": "This is Haskell's interpretation linking Bellori's passages to neo-classicism; its existing p. 160 continuation link is preserved.",
    "st-chp6-p159-raphael-devotion": "Haskell says Maratta and Chiari shared devotion to Raphael and describes Maratta's fresco restoration as one expression; preserve the collective coreference and evaluative qualification.",
    "st-chp6-p159-sacchi-unpublished-life": "This records Bellori's reported authorship of an unpublished life of Andrea Sacchi; the scan reads 'Life', while the S0 OCR reads 'Use'.",
}

FALSE_NOTES = {
    "st-chp6-p159-bellori-consistent-view": "Haskell's evaluative assessment of Bellori's consistency, clarity, authority and role as transmitter rather than originator; no specific entity relation is asserted.",
    "st-chp6-p159-bellori-critical-priority": "This is Haskell's account of Bellori's critical method and priorities, not a specific entity relation candidate.",
    "st-chp6-p159-bellori-influence": "After the comparative claims are split into explicit source-attributed relations, this row records Haskell's general description of Bellori as dominant in artistic circles.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def add_row(base, statement_id, subject, object_, predicate, claim, quote, start, end, mentioned, copy_footnotes=False, qualification=None):
    row = {k: copy.deepcopy(base[k]) for k in ("segment_id", "origin", "source_file") if k in base}
    row.update({"statement_id": statement_id, "subject_candidate_id": subject, "object_candidate_id": object_, "predicate": predicate, "original_quote": quote})
    q = {}
    row["qualifiers"] = q
    if copy_footnotes:
        for key, value in base.get("qualifiers", {}).items():
            if key.startswith("footnote_"):
                q[key] = copy.deepcopy(value)
    q.update({
        "printed_page": "159",
        "pdf_physical_page": 14,
        "source_line_start": start,
        "source_line_end": end,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial historical account",
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": True,
        "relation_candidate_note": "Source-grounded S2 relation candidate; preserve Haskell's attribution and qualifications. No formal S6 edge is created.",
    })
    if qualification:
        q["qualification"] = qualification
    if not object_:
        q["open_endpoint_reason"] = "The comparator or target group is not individually identified in this passage; retain the source-defined open endpoint without inventing members."
    return row


def build():
    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        if sha(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {sid for sid, row in by_id.items() if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.159 unset target set changed: {sorted(unset ^ TARGETS)}")

    _, candidates, _ = read_csv(CANDIDATES)
    candidate_ids = {r["candidate_id"] for r in candidates}
    required = {"cand-0018", "cand-0034", "cand-0272", "cand-0274", "cand-0277", "cand-0295", "cand-0544", "cand-0576", "cand-0932", "cand-1526", "cand-1984", "cand-2098", "cand-2318", "cand-2704", "cand-3403", "cand-6011", "cand-6420", "cand-6424", "cand-6425", "cand-6426", "cand-6427", "cand-6428", "cand-6433", "cand-6434", "cand-6436"}
    if not required <= candidate_ids:
        raise SystemExit(f"required p.159 candidate missing: {sorted(required - candidate_ids)}")
    if set(TRUE_NOTES) | set(FALSE_NOTES) != TARGETS:
        raise SystemExit("classification map does not cover exactly the p.159 target set")

    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    for sid, note in FALSE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    # Atomicize only explicit multi-entity relations; preserve the source's OCR and all prior cross-page links.
    l29, l30, l31, l32, l34, l35, l36, l37, l38 = (source_lines[i - 1] for i in (29, 30, 31, 32, 34, 35, 36, 37, 38))
    q_bernini = l34[l34.index("Bernini a few casual mentions"):l34.index(". He wrote", l34.index("Bernini a few casual mentions"))]
    q_agucchi = l31[l31.index("already been elaborated"):l31.index(". After the Renaissance")]
    q_jesuits = l29[:l29.index(", the popes")]
    q_popes = l29[:l29.index(" or any of the other bodies")]
    q_other = l29
    q_lives_preface = l29[l29.index("in 1672"):l29.index(". From then")]
    q_carracci = l31[l31.index("rescued by"):] + "\n" + l32[:l32.index(" They had")]
    q_antique = l32[l32.index("a profound study of the antique"):l32.index(" and of the great masters")]
    q_masters = l32[l32.index("a profound study of the antique"):l32.index(".", l32.index("a profound study of the antique"))]
    q_appeal = l36[l36.index("Maratta, Sacchi"):l36.index(". In 1652")]
    q_chiari = l36[l36.index("It was to Bellori that"):l36.index(".3", l36.index("It was to Bellori that"))]
    q_poussin = l34[l34.index("Nicolas Poussin"):l34.index(". It was, therefore")]
    q_pupil = l36[l36.index("Maratta and his pupil Giuseppe Chiari"):l36.index(" went for iconographical")]
    q_devotion = l36[l36.index("The devout love for Raphael"):] + "\n" + l37[:l37.index(". Furiously")]
    q_fresco = l36[l36.index("expressed by Maratta"):l36.index(" and Bellori")]
    q_vatican = l36[l36.index("the frescoes in"):l36.index(" and Bellori")]
    q_farnesina = q_vatican
    title_at = l36.index("Descrizione delle Immagini dipinte da")
    title_start = l36.rfind("Bellori", 0, title_at)
    q_descrizione = l36[title_start:] + "\n" + l37[:l37.index(". Furiously")]

    # Bellori's Lives, rather than Bellori as a person, is the subject of the two coverage statements.
    algardi = by_id["st-chp6-p159-algardi-bernini-treatment"]
    algardi["subject_candidate_id"] = "cand-0277"
    algardi["object_candidate_id"] = "cand-0034"
    algardi["predicate"] = "includes_full_scale_life_of"
    algardi["original_quote"] = l34[l34.index("The sculptor Algardi"):l34.index("; Bernini")]
    algardi["qualifiers"]["claim"] = "Haskell says Bellori's Lives gave Algardi a full-scale life."
    algardi["qualifiers"]["mentioned_candidate_ids"] = ["cand-0277", "cand-0034"]

    attack = by_id["st-chp6-p159-attacks-raphael-critics"]
    attack["object_candidate_id"] = None
    attack["predicate"] = "attacked_unnamed_opponents_of_raphael_cult"
    attack["qualifiers"]["open_endpoint_reason"] = "The opponents who rejected the cult are unnamed. Raphael and the cult remain mentions, not the target of the attack relation."

    influence = by_id["st-chp6-p159-bellori-influence"]
    influence["object_candidate_id"] = None
    influence["predicate"] = "described_as_dominant_figure_in_artistic_circles"
    influence["original_quote"] = l29[l29.index("From then onwards he was a dominant figure"):l29.index(", more influential")]
    influence["qualifiers"]["claim"] = "Haskell describes Bellori as a dominant figure in artistic circles from 1672 onward."
    influence["qualifiers"]["mentioned_candidate_ids"] = ["cand-0272"]
    influence["qualifiers"]["coreference_map"] = [{"surface": "he", "source_line": 29, "resolves_to_candidate_ids": ["cand-0272"], "note": "Continues the p. 158 Bellori passage."}]
    influence["qualifiers"]["time_scope"] = "From the 1672 publication onward, as signalled by 'From then onwards'."

    lives = by_id["st-chp6-p159-bellori-lives-1672-preface"]
    lives["predicate"] = "published_lives_in_1672"
    lives["qualifiers"]["claim"] = "Haskell says Bellori published the Lives in 1672."
    lives["qualifiers"]["date"] = "1672"

    rescue = by_id["st-chp6-p159-carracci-rescue"]
    rescue["qualifiers"]["claim"] = "Haskell credits Annibale Carracci with rescuing art from mannerism."
    rescue["qualifiers"]["mentioned_candidate_ids"] = ["cand-0576", "cand-6426"]

    return_row = by_id["st-chp6-p159-carracci-return-to-models"]
    return_row["predicate"] = "returned_to_nature"
    return_row["qualifiers"]["claim"] = "Haskell says the Bolognese followers of Carracci turned back to nature."
    return_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-6427", "cand-6428"]

    maratta = by_id["st-chp6-p159-maratta-appeal-pupil"]
    maratta["predicate"] = "pupil_of"
    maratta["qualifiers"]["claim"] = "Haskell identifies Carlo Maratta as Andrea Sacchi's pupil."
    maratta["qualifiers"]["mentioned_candidate_ids"] = ["cand-1526", "cand-2318"]

    chiari_advice = by_id["st-chp6-p159-chiari-advice"]
    chiari_advice["qualifiers"]["claim"] = "Haskell says Maratta went to Bellori for iconographical advice and probably other advice on difficult commissions."
    chiari_advice["qualifiers"]["mentioned_candidate_ids"] = ["cand-1526", "cand-0272"]

    poussin = by_id["st-chp6-p159-poussin-friend-influence"]
    poussin["predicate"] = "great_friend_of"
    poussin["qualifiers"]["claim"] = "Haskell calls Nicolas Poussin Bellori's great friend."
    poussin["qualifiers"]["mentioned_candidate_ids"] = ["cand-1984", "cand-0272"]

    additions = [
        add_row(algardi, "st-chp6-p159-lives-mentions-bernini-casually", "cand-0277", "cand-0295", "mentions_only_casually", "Haskell says Bellori's Lives gave Bernini only a few casual mentions.", q_bernini, 34, 34, ["cand-0277", "cand-0295"]),
        add_row(by_id["st-chp6-p159-bellori-ideal-criterion"], "st-chp6-p159-agucchi-elaborated-ideal", "cand-0018", "cand-6420", "elaborated_ideal_concept", "Haskell says Monsignor Agucchi had already elaborated the Ideal concept.", q_agucchi, 31, 31, ["cand-0018", "cand-6420"]),
        add_row(influence, "st-chp6-p159-bellori-more-influential-than-jesuits", "cand-0272", "cand-3403", "more_influential_than", "Haskell says Bellori was more influential than the Jesuits in the short and long run.", q_jesuits, 29, 29, ["cand-0272", "cand-3403"]),
        add_row(influence, "st-chp6-p159-bellori-more-influential-than-popes", "cand-0272", "cand-6424", "more_influential_than", "Haskell says Bellori was more influential than the popes in the short and long run.", q_popes, 29, 29, ["cand-0272", "cand-6424"]),
        add_row(influence, "st-chp6-p159-bellori-more-influential-than-other-bodies", "cand-0272", None, "more_influential_than_other_style_forming_bodies", "Haskell says Bellori was more influential than other bodies held to have moulded stylistic developments.", q_other, 29, 29, ["cand-0272"]),
        add_row(lives, "st-chp6-p159-lives-includes-prefatory-lecture", "cand-0277", "cand-6419", "includes_earlier_lecture_as_preface", "Haskell says Bellori included an earlier lecture as a preface to the Lives.", q_lives_preface, 29, 29, ["cand-0277", "cand-6419"]),
        add_row(rescue, "st-chp6-p159-bolognese-followers-rescued-mannerism", "cand-6427", "cand-6426", "credited_with_rescuing_art_from_mannerism", "Haskell credits Carracci's Bolognese followers with helping rescue art from mannerism.", q_carracci, 31, 32, ["cand-6427", "cand-6426"]),
        add_row(return_row, "st-chp6-p159-bolognese-followers-studied-antiquity", "cand-6427", "cand-6011", "studied_antiquity", "Haskell says Carracci's Bolognese followers undertook profound study of the antique.", q_antique, 32, 32, ["cand-6427", "cand-6011"]),
        add_row(return_row, "st-chp6-p159-bolognese-followers-studied-raphael", "cand-6427", "cand-2098", "studied_great_masters_including_raphael", "Haskell says Carracci's Bolognese followers studied the great masters, especially Raphael.", q_masters, 32, 32, ["cand-6427", "cand-2098"]),
        add_row(maratta, "st-chp6-p159-maratta-appealed-to-bellori", "cand-1526", "cand-0272", "appealed_to", "Haskell says Maratta most appealed to Bellori among the artists of his time.", q_appeal, 36, 36, ["cand-1526", "cand-0272"]),
        add_row(chiari_advice, "st-chp6-p159-chiari-pupil-of-maratta", "cand-6436", "cand-1526", "pupil_of", "Haskell identifies Giuseppe Chiari as Maratta's pupil.", q_pupil, 36, 36, ["cand-6436", "cand-1526"]),
        add_row(chiari_advice, "st-chp6-p159-chiari-sought-advice-from-bellori", "cand-6436", "cand-0272", "sought_iconographical_advice_from", "Haskell says Giuseppe Chiari went to Bellori for iconographical and probably other advice on difficult commissions.", q_chiari, 36, 36, ["cand-6436", "cand-0272"], copy_footnotes=True, qualification="The iconographical advice is explicit; Haskell marks other advice as probable. The p. 159 note 3 link is retained."),
        add_row(poussin, "st-chp6-p159-poussin-inspired-lives", "cand-1984", "cand-0277", "inspired_ideas_in", "Haskell says Poussin unquestionably inspired many ideas in Bellori's book.", q_poussin, 34, 34, ["cand-1984", "cand-0277"]),
        add_row(by_id["st-chp6-p159-raphael-devotion"], "st-chp6-p159-chiari-devotion-to-raphael", "cand-6436", "cand-2098", "devoutly_loved", "Haskell includes Giuseppe Chiari among the two men who felt devout love for Raphael.", q_devotion, 36, 37, ["cand-6436", "cand-2098"], qualification="The phrase 'both men' refers to Carlo Maratta and Giuseppe Chiari in the immediately preceding sentence."),
        add_row(by_id["st-chp6-p159-raphael-devotion"], "st-chp6-p159-maratta-restored-raphael-frescoes", "cand-6434", "cand-1526", "restored_by", "Haskell reports that Maratta restored the unspecified Raphael fresco group at the Vatican and Farnesina.", q_fresco, 36, 36, ["cand-6434", "cand-1526"], qualification="The plural fresco group is unnamed; this statement records the restoration relation only."),
        add_row(by_id["st-chp6-p159-raphael-devotion"], "st-chp6-p159-raphael-frescoes-at-vatican", "cand-6434", "cand-2704", "located_at", "Haskell locates the unspecified Raphael fresco group at the Vatican.", q_vatican, 36, 36, ["cand-6434", "cand-2704"]),
        add_row(by_id["st-chp6-p159-raphael-devotion"], "st-chp6-p159-raphael-frescoes-at-farnesina", "cand-6434", "cand-6433", "located_at", "Haskell locates the unspecified Raphael fresco group at the Farnesina.", q_farnesina, 36, 36, ["cand-6434", "cand-6433"]),
        add_row(by_id["st-chp6-p159-bellori-descrizione"], "st-chp6-p159-descrizione-expresses-raphael-devotion", "cand-0274", "cand-2098", "expressed_devotion_to", "Haskell presents Bellori's Descrizione as an expression of devotion to Raphael.", q_devotion, 36, 37, ["cand-0274", "cand-2098"]),
    ]

    by_id["st-chp6-p159-raphael-devotion"]["original_quote"] = q_devotion
    for row in additions:
        if row["statement_id"] == "st-chp6-p159-lives-includes-prefatory-lecture":
            row["qualifiers"]["date"] = "1672 publication; the lecture was delivered some years earlier."
            row["qualifiers"]["coreference_map"] = [{"surface": "he", "source_line": 29, "resolves_to_candidate_ids": ["cand-0272"], "note": "Continues the p. 158 Bellori passage."}]
        elif row["statement_id"].startswith("st-chp6-p159-bellori-more-influential-"):
            row["qualifiers"]["time_scope"] = "From the 1672 publication onward, as signalled by 'From then onwards'."
            row["qualifiers"]["coreference_map"] = [{"surface": "he", "source_line": 29, "resolves_to_candidate_ids": ["cand-0272"], "note": "Continues the p. 158 Bellori passage."}]
        elif row["statement_id"] == "st-chp6-p159-maratta-appealed-to-bellori":
            row["qualifiers"]["coreference_map"] = [{"surface": "him", "source_line": 36, "resolves_to_candidate_ids": ["cand-0272"], "note": "Bellori is the antecedent in the paragraph."}]
        elif row["statement_id"] in {"st-chp6-p159-maratta-restored-raphael-frescoes", "st-chp6-p159-raphael-frescoes-at-vatican", "st-chp6-p159-raphael-frescoes-at-farnesina"}:
            row["qualifiers"]["pdf_print_corrections"] = ["Print p.159 reads 'the Vatican'; S0 OCR has an extra apostrophe in 'the'Vatican'."]
        elif row["statement_id"] == "st-chp6-p159-descrizione-expresses-raphael-devotion":
            row["qualifiers"]["pdf_print_corrections"] = ["Print p.159 reads 'Raffaello d'Urbino'; S0 OCR inserts a space after the apostrophe."]

    # Separate the source's mixed comparative statement from Bellori's general authorial characterization.
    other = next(r for r in additions if r["statement_id"] == "st-chp6-p159-bellori-more-influential-than-other-bodies")
    other["qualifiers"]["open_endpoint_reason"] = "The remaining comparator is described only as 'other bodies' said to mould stylistic developments; no individual body is named."
    by_id["st-chp6-p159-sacchi-unpublished-life"]["qualifiers"]["pdf_print_corrections"] = ["Print p.159 reads 'a Life of Andrea Sacchi'; S0 OCR reads 'a Use of Andrea Sacchi' and remains unchanged."]
    by_id["st-chp6-p159-attacks-raphael-critics"]["qualifiers"]["pdf_print_corrections"] = ["Print p.159 reads 'the cult'; S0 OCR has an extra apostrophe in 'the'cult'."]
    by_id["st-chp6-p159-raphael-devotion"]["qualifiers"]["pdf_print_corrections"] = ["Print p.159 reads 'the Vatican'; S0 OCR has an extra apostrophe in 'the'Vatican'."]

    for row in additions:
        q = row["qualifiers"]
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1:end]):
            raise SystemExit(f"new quote is not anchored: {row['statement_id']}")
        refs = set(q.get("mentioned_candidate_ids", [])) | {cid for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")) if cid}
        if refs - candidate_ids:
            raise SystemExit(f"new candidate reference missing: {row['statement_id']} -> {sorted(refs - candidate_ids)}")

    coverage_fields, coverage, coverage_bom = read_csv(COVERAGE)
    cov = next((r for r in coverage if r["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected coverage state: {cov}")
    cov["note"] = (
        "印本p.159正文L29–38完成S2语义裁决：分类Bellori的批评立场、Lives书目内容、艺术家关系及风格概念判断；"
        "拆分Algardi/Bernini覆盖、Bellori对Jesuits/教皇/其他风格塑造机构的比较、Carracci追随者的艺术史角色与学习对象、"
        "Maratta/Chiari师承和咨询、Poussin对Lives的影响，以及Raphael崇拜、壁画地点和Bellori《Descrizione》关系。"
        "匿名Raphael批评者和泛称机构保持开放端点；引语层级与Haskell评价保留。扫描校正art-historical、Life、the Vatican及the cult，只记S2不改S0；"
        "p.159 L38的neo-classicism句维持至p.160续接。"
    )

    insert_after = {
        "st-chp6-p159-algardi-bernini-treatment": [additions[0]],
        "st-chp6-p159-bellori-ideal-criterion": [additions[1]],
        "st-chp6-p159-bellori-influence": additions[2:5],
        "st-chp6-p159-bellori-lives-1672-preface": [additions[5]],
        "st-chp6-p159-carracci-rescue": [additions[6]],
        "st-chp6-p159-carracci-return-to-models": additions[7:9],
        "st-chp6-p159-maratta-appeal-pupil": [additions[9]],
        "st-chp6-p159-chiari-advice": additions[10:12],
        "st-chp6-p159-poussin-friend-influence": [additions[12]],
        "st-chp6-p159-raphael-devotion": additions[13:17],
        "st-chp6-p159-bellori-descrizione": [additions[17]],
    }
    output_rows = []
    for row in statements:
        output_rows.append(row)
        output_rows.extend(insert_after.get(row["statement_id"], []))
    ids = [r["statement_id"] for r in output_rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate statement ID after p.159 split")
    segment_rows = [r for r in output_rows if r.get("segment_id") == SEGMENT]
    true_count = sum(r["qualifiers"].get("relation_candidate") is True for r in segment_rows)
    false_count = sum(r["qualifiers"].get("relation_candidate") is False for r in segment_rows)
    unset_count = sum(r["qualifiers"].get("relation_candidate") is None for r in segment_rows)
    if (len(segment_rows), true_count, false_count, unset_count) != (45, 42, 3, 0):
        raise SystemExit(f"unexpected p.159 segment totals: {(len(segment_rows), true_count, false_count, unset_count)}")

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in output_rows) + "\n").encode("utf-8"),
        COVERAGE: csv_bytes(coverage_fields, coverage, coverage_bom),
    }
    summary = {"segment": SEGMENT, "classified_existing": len(TARGETS), "new_atomic_statements": len(additions), "relation_candidates_after": true_count, "non_relational_after": false_count, "unset_after": unset_count, "mode": "dry-run"}
    return outputs, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    outputs, summary = build()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
