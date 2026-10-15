from __future__ import annotations

import argparse
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l69-76"
TARGETS = {
    "st-chp6-p152-alexander-complains-poverty",
    "st-chp6-p152-alexander-financial-resources",
    "st-chp6-p152-independent-artists-suffer",
    "st-chp6-p152-querini-1668-criticises-construction",
    "st-chp6-p152-querini-exaggeration-qualified",
    "st-chp6-p152-quirinal-decoration-continues",
    "st-chp6-p152-roman-plague-1656",
    "st-chp6-p152-rosa-1662-and-1664-letters",
    "st-chp6-p152-sagredo-1661-building-and-depopulation",
}
CANDIDATE_IDS = [f"cand-{n}" for n in range(11982, 11990)]
NEW_MENTION_IDS = [
    "m-chp6-p152-venetian-ambassadors",
    "m-chp6-p152-building-policy",
    "m-chp6-p152-querini-buildings",
    "m-chp6-p152-roads",
    "m-chp6-p152-predecessors",
    "m-chp6-p152-conclave",
    "m-chp6-p152-urban-measures",
    "m-chp6-p152-malaria",
]
NEW_STATEMENT_IDS = [
    "st-chp6-p152-ambassadors-observe-portico-expenses",
    "st-chp6-p152-economic-decline-continues",
    "st-chp6-p152-building-policy-contrasted-with-city-state",
    "st-chp6-p152-long-term-economic-effects-serious",
    "st-chp6-p152-querini-porticos-useless",
    "st-chp6-p152-querini-architecture-weaknesses-blamed-on-bernini",
    "st-chp6-p152-querini-columns-form-precinct-for-church",
    "st-chp6-p152-querini-predicts-leonine-city-uninhabitable",
    "st-chp6-p152-querini-predicts-vatican-abandoned",
    "st-chp6-p152-querini-predicts-conclave-impossible",
    "st-chp6-p152-querini-predicts-malaria-from-urban-measures",
    "st-chp6-p152-querini-reports-million-scudi-spent",
    "st-chp6-p152-desolation-real-different-origins",
    "st-chp6-p152-rosa-1664-no-commissions",
    "st-chp6-p152-rosa-1664-fears-worsening-war-news",
    "st-chp6-p152-alexander-repairs-roman-roads",
    "st-chp6-p152-alexander-surpasses-papal-predecessors",
    "st-chp6-p152-colonnades-encircle-piazza",
    "st-chp6-p152-colonnades-recall-ancient-rome",
    "st-chp6-p152-colonnade-halfway-complete-estimate",
    "st-chp6-p152-sagredo-defers-advisability-judgment",
    "st-chp6-p152-rome-buildings-population-observation",
]
EXPECTED_HASHES = {
    STATEMENTS: "f99477e6e6b2230b9f64c7e0a59d2862398402b6ee8797856947414dda05042b",
    CANDIDATES: "d356db10b1615e7374c240239dfd8f7993d3150c49c34ba251b81519e9307d43",
    MENTIONS: "11296e67bca50f2fb9ad58e2f4b457b98253ce7a7caa1d8d7f01a2a601f624ba",
    COVERAGE: "3ddfb5e10a74e92992ae28b5f4df4415b57b73a315b3f623fe689f04e206f1a1",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
SEGMENT_SHA256 = "e9e7838f2b0aa2aeace4afdf4e86771725c67645172fdb45c80d9a5b1864a555"
BACKUP_SUFFIX = ".bak-s2-chp6-p152-semantics-20261013"
TRUE_NOTE = "This is a source-attributed relation candidate retained at S2; it does not create a formal S6 edge."
FALSE_NOTE = "This is a source-attributed descriptive, evaluative, or scalar claim, not a relation between represented entities."
FOOTNOTE_KEYS = (
    "footnote_markers", "footnote_link_status", "footnote_segment", "footnote_target_line",
    "footnote_printed_page", "footnote_citation_statement_ids", "footnote_pending",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def read_csv(path: Path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    os.replace(temp, path)


def extract(source_lines, start_line: int, end_line: int, first: str, last: str) -> str:
    span = "\n".join(source_lines[start_line - 1:end_line])
    start = span.find(first)
    if start < 0:
        raise SystemExit(f"quote start not found at L{start_line}: {first!r}")
    if first == last:
        return span[start:start + len(first)]
    end = span.find(last, start + len(first))
    if end < 0:
        raise SystemExit(f"quote end not found at L{start_line}-L{end_line}: {last!r}")
    return span[start:end + len(last)]


def make_candidate(cid, name, kind, detail, line):
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def add_mention(mid, cid, surface, note, text):
    at = text.find(surface)
    if at < 0 or text.find(surface, at + 1) >= 0:
        raise SystemExit(f"mention must occur exactly once: {mid} / {surface!r}")
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(at),
            "end_char": str(at + len(surface)), "note": note}


def statement_row(sid, subject, object_, predicate, claim, quote, relation, qualification,
                  mentioned, start, end, speaker, text_layer, note=None, extra=None):
    qualifiers = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": "152", "pdf_physical_page": 7,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": note or (TRUE_NOTE if relation else FALSE_NOTE),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
    }


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[68:76])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256 or source_lines[68].strip() != "[Page 152]":
        raise SystemExit("p.152 source segment hash/page mismatch")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in source table")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.152 unset target set changed: {sorted(unset)}")
    if any(sid in by_id for sid in NEW_STATEMENT_IDS):
        raise SystemExit("planned p.152 statement ID already exists")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    vfields, coverage, vbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if any(cid in candidate_ids for cid in CANDIDATE_IDS) or any(mid in mention_ids for mid in NEW_MENTION_IDS):
        raise SystemExit("planned p.152 candidate or mention ID already exists")
    numeric_ids = [int(row["candidate_id"].split("-")[1]) for row in candidates
                   if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()]
    if max(numeric_ids) != 11981:
        raise SystemExit(f"candidate sequence changed: max={max(numeric_ids)}")
    cov = {row["segment_id"]: row for row in coverage}.get(SEGMENT)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.152 coverage state: {cov}")

    candidates_to_add = [
        make_candidate("cand-11982", "Venetian ambassadors addressed by Alexander VII (unnamed group)", "term",
            "The source identifies only a collective of Venetian ambassadors to whom Alexander VII complained of poverty; no individuals or mission dates are supplied.", 70),
        make_candidate("cand-11983", "Alexander VII's Roman building policy (Haskell's source-defined program)", "term",
            "Haskell contrasts the Pope's spectacular building policy with the general state of Rome; Querini's quoted criticism refers to the associated building programme. Do not treat Querini's predicted outcomes as established facts.", 70),
        make_candidate("cand-11984", "General state of Rome under Alexander VII (Haskell's source-defined condition)", "term",
            "The abstract urban condition contrasted with Alexander VII's building policy; no independent measure is supplied in this passage.", 70),
        make_candidate("cand-11985", "Roads in Rome described by Niccolò Sagredo (unnamed group)", "place",
            "Sagredo's 1661 quoted report says Alexander VII attended to repairing roads; no individual roads are named.", 70),
        make_candidate("cand-11986", "Papal predecessors compared with Alexander VII in Sagredo's report (unnamed group)", "term",
            "Sagredo says Alexander VII surpassed his predecessors in beautifying Rome; the predecessors are not named or individually enumerated.", 70),
        make_candidate("cand-11987", "Papal conclave potentially held at the Vatican in Querini's prediction", "event",
            "A hypothetical conclave mentioned only as an event Querini predicts may become impossible to hold at the Vatican; this does not assert that such a conclave occurred.", 74),
        make_candidate("cand-11988", "Urban measures in Querini's malaria prediction (house razing, fountain water and fires)", "procedure",
            "A source-defined group of measures that Querini says would lead to malaria: razing houses, increasing water for fountains, and extinguishing fires.", 74),
        make_candidate("cand-11989", "Malaria risk in Querini's urban-planning argument", "term",
            "Malaria is named as a predicted consequence in Querini's quoted criticism; the passage does not report an outbreak caused by these measures.", 74),
    ]
    if any(row["candidate_id"] in candidate_ids for row in candidates_to_add):
        raise SystemExit("planned p.152 candidate already exists")

    segment_candidates = candidate_ids | set(CANDIDATE_IDS)
    new_mentions = [
        add_mention(NEW_MENTION_IDS[0], "cand-11982", "the Venetian ambassadors",
                    "Unnamed collective addressed by Alexander VII; keep separate from Venice as a political entity.", segment_text),
        add_mention(NEW_MENTION_IDS[1], "cand-11983", "his spectacular building policy",
                    "Alexander VII's source-defined urban building programme, contrasted with Rome's general condition.", segment_text),
        add_mention(NEW_MENTION_IDS[2], "cand-11983", "the putting up of buildings",
                    "Querini's phrase for the building programme he criticizes; relation remains attributed to his polemical quotation.", segment_text),
        add_mention(NEW_MENTION_IDS[3], "cand-11985", "the roads",
                    "Unnamed roads in Rome referred to in Sagredo's 1661 report.", segment_text),
        add_mention(NEW_MENTION_IDS[4], "cand-11986", "his predecessors",
                    "Unnamed papal predecessors in Sagredo's comparison with Alexander VII.", segment_text),
        add_mention(NEW_MENTION_IDS[5], "cand-11987", "the conclave",
                    "Hypothetical future conclave in Querini's prediction; the passage does not say one occurred.", segment_text),
        add_mention(NEW_MENTION_IDS[6], "cand-11988", "the razing of houses, the increase in water for fountains and the extinction of fires",
                    "The three urban measures Querini groups as predicted causes of malaria.", segment_text),
        add_mention(NEW_MENTION_IDS[7], "cand-11989", "malaria",
                    "Named as a predicted consequence in Querini's quoted claim, not as an outcome established here.", segment_text),
    ]
    by_mid = {row["mention_id"]: row for row in mentions}
    state_mention = by_mid.get("m-chp6-p152-179")
    if not state_mention or state_mention["candidate_id"] != "cand-4490" or state_mention["surface_form"] != "the city":
        raise SystemExit("p.152 general-city mention changed")
    state_span = "general state of the city"
    state_at = segment_text.find(state_span)
    if state_at < 0 or segment_text.find(state_span, state_at + 1) >= 0:
        raise SystemExit("p.152 general-state phrase is not unique")
    state_mention.update({
        "candidate_id": "cand-11984", "surface_form": state_span,
        "start_char": str(state_at), "end_char": str(state_at + len(state_span)),
        "note": "The phrase names the abstract urban condition contrasted with the building policy, not Rome as a location alone.",
    })
    for mention in new_mentions:
        if mention["candidate_id"] not in segment_candidates:
            raise SystemExit(f"new mention candidate missing: {mention['mention_id']}")

    def q(start, end, first, last):
        return extract(source_lines, start, end, first, last)

    # Retain only the exact proposition represented by each existing statement.
    rosa_footnote = {key: by_id["st-chp6-p152-rosa-1662-and-1664-letters"]["qualifiers"][key]
                     for key in FOOTNOTE_KEYS if key in by_id["st-chp6-p152-rosa-1662-and-1664-letters"]["qualifiers"]}
    existing_updates = {
        "st-chp6-p152-alexander-complains-poverty": {
            "subject": "cand-0665", "object": "cand-11982", "predicate": "alexander_vii_complained_of_poverty_to_venetian_ambassadors",
            "claim": "Haskell reports that Alexander VII complained of poverty to the unnamed Venetian ambassadors.",
            "relation": True, "qualification": "The ambassadors are an unnamed collective; footnote 1 supplies a secondary citation that has not been independently reviewed.",
            "mentioned": ["cand-0665", "cand-11982"], "lines": (70, 70), "quote": (70, 70, "To the Venetian ambassadors", "his poverty,1"),
            "speaker": "Haskell reporting Alexander VII", "layer": "authorial narrative with reported speech",
        },
        "st-chp6-p152-alexander-financial-resources": {
            "subject": "cand-0665", "object": None, "predicate": "alexander_vii_accumulated_resources_remained_plentiful_despite_financial_drains",
            "claim": "Haskell says that despite tremendous drains on Alexander VII's finances, his accumulated resources remained plentiful.",
            "relation": False, "qualification": "The sentence completes the p.151 fragment; it is a source-reported financial condition without a second represented entity or quantitative measure.",
            "mentioned": ["cand-0665"], "lines": (70, 70), "quote": (70, 70, "finances, his accumulated resources", "still plentiful."),
            "speaker": "Haskell", "layer": "authorial historical narrative",
            "extra": {"continuation_status": "complete", "continued_from_segment_id": "chp-6:06_CHP-6_sec_i:l59-67",
                      "continued_from_source_line": 67, "continuation_resolved_from_statement_id": "st-chp6-p151-economic-drains-partial"},
        },
        "st-chp6-p152-independent-artists-suffer": {
            "subject": "cand-6319", "object": "cand-6247", "predicate": "independent_artists_suffered_most_from_rome_impoverishment",
            "claim": "Haskell says the independent artists suffered most from the impoverishment of Rome.",
            "relation": True, "qualification": "This is Haskell's generalization about an unnamed artist group; no individual artists are identified.",
            "mentioned": ["cand-6319", "cand-6247"], "lines": (75, 75), "quote": (75, 75, "As usual it was the independent artists", "impoverishment of Rome."),
            "speaker": "Haskell", "layer": "authorial historical interpretation",
        },
        "st-chp6-p152-querini-1668-criticises-construction": {
            "subject": "cand-11983", "object": "cand-4490", "predicate": "querini_claims_alexander_vii_buildings_destroyed_rather_than_improved_rome",
            "claim": "Querini claims that Alexander VII's building programme destroyed rather than added to Rome.",
            "relation": True, "qualification": "This is Querini's polemical claim in Haskell's quotation, not an accepted account of the buildings' effects.",
            "mentioned": ["cand-2087", "cand-11983", "cand-4490"], "lines": (73, 73), "quote": (73, 73, "has been the putting up of buildings", "capital of the world."),
            "speaker": "Giacomo Querini, quoted by Haskell", "layer": "nested diplomatic quotation",
        },
        "st-chp6-p152-querini-exaggeration-qualified": {
            "subject": "cand-2087", "object": None, "predicate": "haskell_says_querini_exaggerated_for_political_reasons",
            "claim": "Haskell says Querini was exaggerating for political reasons.",
            "relation": False, "qualification": "The motive attribution is Haskell's assessment, not Querini's stated explanation.",
            "mentioned": ["cand-2087"], "lines": (75, 75), "quote": (75, 75, "Querini was exaggerating", "for political reasons."),
            "speaker": "Haskell", "layer": "authorial historical assessment",
        },
        "st-chp6-p152-quirinal-decoration-continues": {
            "subject": "cand-6312", "object": "cand-6318", "predicate": "quirinal_decoration_continued_throughout_1656_plague_year",
            "claim": "Haskell says he is specifically told that decoration work at the Quirinal continued throughout the plague year.",
            "relation": True, "qualification": "Footnote 4 points to Bellori; the cited source has not yet been independently reviewed.",
            "mentioned": ["cand-6312", "cand-6318"], "lines": (75, 75), "quote": (75, 75, "Though we are specifically told", "this terrible year,4"),
            "speaker": "Haskell reporting another account", "layer": "authorial narrative reporting another account",
        },
        "st-chp6-p152-roman-plague-1656": {
            "subject": "cand-6318", "object": "cand-4490", "predicate": "roman_plague_of_1656_reached_rome_from_naples",
            "claim": "Haskell says the major plague moving north from Naples struck Rome a few months after 1656 began, at the start of Alexander VII's reign.",
            "relation": True, "qualification": "Retain Haskell's chronology and description; the passage does not supply a more exact date.",
            "mentioned": ["cand-6318", "cand-3462", "cand-3534", "cand-4490", "cand-0665"],
            "lines": (75, 75), "quote": (75, 75, "In 1656 the last great plague", "reign."),
            "speaker": "Haskell", "layer": "authorial historical narrative",
        },
        "st-chp6-p152-rosa-1662-and-1664-letters": {
            "subject": "cand-2236", "object": None, "predicate": "rosa_reported_public_talk_of_reform_and_retrenchment_in_1662",
            "claim": "Salvator Rosa says in 1662 that people had been talking only of reforms and retrenchment for seven months.",
            "relation": False, "qualification": "The recipients and exact document are not identified; this is Rosa's reported observation, not an independently verified measure of public opinion.",
            "mentioned": ["cand-2236"], "lines": (75, 75), "quote": (75, 75, "For seven months now people have been talking", "wrote"),
            "speaker": "Salvator Rosa, quoted by Haskell", "layer": "nested quotation from an unidentified written source",
            "remove_footnote": True,
            "extra": {"ocr_corrections": [{"source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "source_line": 75,
                      "ocr": "òf", "print": "of", "basis": "CHP-6.pdf physical page 7."}]},
        },
        "st-chp6-p152-sagredo-1661-building-and-depopulation": {
            "subject": "cand-0665", "object": "cand-4490", "predicate": "sagredo_reports_alexander_vii_attended_to_beautifying_rome",
            "claim": "In a 1661 report, Niccolò Sagredo says Alexander VII had long paid particular attention to beautifying Rome.",
            "relation": True, "qualification": "This is Sagredo's report as quoted by Haskell; footnote 2 is linked but has not been independently reviewed.",
            "mentioned": ["cand-2327", "cand-0665", "cand-4490"], "lines": (70, 70), "quote": (70, 70, "The Pope has long paid particular attention", "beautifying the city"),
            "speaker": "Niccolò Sagredo, quoted by Haskell", "layer": "nested diplomatic quotation",
        },
    }
    if set(existing_updates) != TARGETS:
        raise SystemExit("p.152 update set does not match all unset targets")

    for sid, spec in existing_updates.items():
        row = by_id[sid]
        quote_spec = spec["quote"]
        quote = q(*quote_spec)
        if norm(quote) not in norm(row.get("original_quote", "")):
            raise SystemExit(f"p.152 quote is not contained in existing source quote: {sid}")
        row["subject_candidate_id"] = spec["subject"]
        row["object_candidate_id"] = spec["object"]
        row["predicate"] = spec["predicate"]
        row["original_quote"] = quote
        qualifiers = row["qualifiers"]
        qualifiers.update({
            "source_line_start": spec["lines"][0], "source_line_end": spec["lines"][1],
            "claim": spec["claim"], "speaker": spec["speaker"], "text_layer": spec["layer"],
            "qualification": spec["qualification"], "mentioned_candidate_ids": spec["mentioned"],
            "relation_candidate": spec["relation"],
            "relation_candidate_note": TRUE_NOTE if spec["relation"] else FALSE_NOTE,
        })
        if spec.get("extra"):
            qualifiers.update(spec["extra"])
        if spec.get("remove_footnote"):
            for key in FOOTNOTE_KEYS:
                qualifiers.pop(key, None)

    def footnote_copy(sid):
        return {key: by_id[sid]["qualifiers"][key] for key in FOOTNOTE_KEYS if key in by_id[sid]["qualifiers"]}

    def new_statement(sid, subject, object_, predicate, claim, quote_spec, relation, qualification,
                      mentioned, speaker, layer, *, start=None, end=None, footnote_from=None,
                      relation_note=None, extra=None):
        qspec = quote_spec
        quote = q(*qspec)
        row = statement_row(
            sid, subject, object_, predicate, claim, quote, relation, qualification,
            mentioned, start or qspec[0], end or qspec[1], speaker, layer,
            note=relation_note, extra=extra,
        )
        if footnote_from:
            row["qualifiers"].update(footnote_copy(footnote_from))
        all_ids = segment_candidates | set(CANDIDATE_IDS)
        if any(cid and cid not in all_ids for cid in [subject, object_]) or not set(mentioned) <= all_ids:
            raise SystemExit(f"new statement candidate reference missing: {sid}")
        return row

    new_statements = [
        new_statement("st-chp6-p152-ambassadors-observe-portico-expenses", "cand-11982", "cand-6307",
            "venetian_ambassadors_observed_bernini_portico_expenses",
            "Haskell says the Venetian ambassadors watched the ruinous expenses of Bernini's portico and cautiously drew conclusions.",
            (70, 70, "and they in turn watched", "obvious conclusions."), True,
            "The ambassadors are an unnamed collective; Haskell reports their observation and inference without supplying the conclusions in detail.",
            ["cand-11982", "cand-0312", "cand-6307"], "Haskell reporting the Venetian ambassadors", "authorial narrative with reported observation",
            relation_note="The passage explicitly links the unnamed ambassadors' observation to the expenses of Bernini's portico."),
        new_statement("st-chp6-p152-economic-decline-continues", "cand-6247", None,
            "economic_decline_continued_without_interruption",
            "Haskell says the economic decline continued without interruption.",
            (70, 70, "Yet the decline continued", "without interruption"), False,
            "This is a scalar historical condition, not a relation between two represented entities.",
            ["cand-6247"], "Haskell", "authorial historical narrative"),
        new_statement("st-chp6-p152-building-policy-contrasted-with-city-state", "cand-11983", "cand-11984",
            "haskell_contrasts_alexander_vii_building_policy_with_general_state_of_rome",
            "Haskell says the contrast between Alexander VII's spectacular building policy and Rome's general condition was starkly apparent.",
            (70, 70, "the contrast between his spectacular building policy", "was starkly apparent."), True,
            "This is Haskell's stated historical contrast; the passage supplies no independent measure of either side.",
            ["cand-11983", "cand-11984"], "Haskell", "authorial historical interpretation",
            relation_note="The sentence explicitly contrasts two source-defined concepts: the papal building policy and the city's general condition."),
        new_statement("st-chp6-p152-long-term-economic-effects-serious", "cand-6247", None,
            "long_term_economic_effects_were_serious",
            "Haskell says the long-term effects on the economy were serious.",
            (75, 75, "the long-term effects on the economy", "were serious."), False,
            "This is Haskell's scalar assessment; no measure or second endpoint is given.",
            ["cand-6247"], "Haskell", "authorial historical interpretation"),
        new_statement("st-chp6-p152-querini-porticos-useless", "cand-2087", None,
            "querini_calls_st_peters_porticos_without_advantage",
            "Querini says the erection of the porticos at St Peter's had no conceivable advantage.",
            (73, 73, "The erection of the porticos at St Peter", "without any conceivable advantage."), False,
            "This is Querini's evaluative judgment in a polemical quotation, not an independently established property of the porticos.",
            ["cand-2087", "cand-6307", "cand-5696"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction"),
        new_statement("st-chp6-p152-querini-architecture-weaknesses-blamed-on-bernini", None, "cand-0312",
            "unnamed_parties_reportedly_blamed_bernini_for_architectural_weaknesses",
            "Querini reports that Bernini had been blamed for obvious weaknesses in the porticos' architecture.",
            (73, 73, "There are obvious weaknesses in the architecture", "Bernini has been blamed."), True,
            "The source reports prior blame but does not identify who made the allegation; it does not establish that Bernini caused the weaknesses.",
            ["cand-2087", "cand-0312", "cand-6307"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction",
            relation_note="The source explicitly reports an attribution of blame to Bernini, while leaving the blaming party unnamed.",
            extra={"open_endpoint_reason": "The source uses the passive 'has been blamed' and identifies no person or group making the allegation."}),
        new_statement("st-chp6-p152-querini-columns-form-precinct-for-church", "cand-6307", "cand-5696",
            "querini_says_colonnade_columns_form_architectural_precinct_for_st_peters",
            "Querini says the three hundred columns, arranged on an oval plan, serve as an architectural precinct for the church of St Peter.",
            (73, 73, "The three hundred columns", "Prince of the Apostles."), True,
            "The number and oval arrangement are Querini's description; the claim is attributed to him and not independently checked here.",
            ["cand-2087", "cand-6307", "cand-5696", "cand-4231"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction",
            relation_note="Querini explicitly describes the columns as an architectural precinct for the church."),
        new_statement("st-chp6-p152-querini-predicts-leonine-city-uninhabitable", "cand-6307", "cand-6317",
            "querini_predicts_porticos_make_leonine_city_uninhabitable",
            "Querini predicts that the porticos would make the Leonine City permanently uninhabitable.",
            (73, 74, "But they will make the", "Leonine city permanently uninhabitable"), True,
            "This is a prediction attributed to Querini, not an established outcome; 'they' refers to the three hundred columns.",
            ["cand-2087", "cand-6307", "cand-6317"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction",
            relation_note="The quotation explicitly predicts an effect of the porticos on the Leonine City."),
        new_statement("st-chp6-p152-querini-predicts-vatican-abandoned", "cand-6307", "cand-3399",
            "querini_predicts_porticos_cause_vatican_abandonment",
            "Querini predicts that the porticos would cause the Vatican to be abandoned.",
            (74, 74, "cause the Vatican to be abandoned", "cause the Vatican to be abandoned"), True,
            "This is a prediction attributed to Querini, not an established outcome; 'they' refers to the three hundred columns.",
            ["cand-2087", "cand-6307", "cand-3399"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction",
            relation_note="The quotation explicitly predicts an effect of the porticos on the Vatican."),
        new_statement("st-chp6-p152-querini-predicts-conclave-impossible", "cand-6307", "cand-11987",
            "querini_predicts_porticos_could_prevent_a_conclave_at_the_vatican",
            "Querini says the porticos might make it impossible to hold a conclave at the Vatican.",
            (74, 74, "perhaps make it impossible to hold the conclave there", "perhaps make it impossible to hold the conclave there"), True,
            "This is a qualified prediction, not a claim that a conclave was prevented; the passage identifies the Vatican as the location.",
            ["cand-2087", "cand-6307", "cand-3399", "cand-11987"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction",
            relation_note="Querini explicitly predicts that the porticos could prevent the named possible event at the Vatican."),
        new_statement("st-chp6-p152-querini-predicts-malaria-from-urban-measures", "cand-11988", "cand-11989",
            "querini_says_urban_measures_would_lead_to_malaria",
            "Querini says house razing, increased water for fountains, and extinguishing fires would lead to malaria.",
            (74, 74, "For the razing of houses", "will lead to malaria."), True,
            "This causal claim is attributed to Querini and is not treated as an established epidemiological outcome.",
            ["cand-2087", "cand-11988", "cand-11989"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction",
            relation_note="The quotation explicitly links a source-defined group of urban measures to the predicted malaria risk."),
        new_statement("st-chp6-p152-querini-reports-million-scudi-spent", "cand-2087", None,
            "querini_reports_over_one_million_scudi_spent_on_building_mistakes",
            "Querini says that more than one million scudi had been spent on what he calls catastrophic mistakes.",
            (74, 74, "All this confirms the worst rumours", "catastrophic mistakes."), False,
            "The sum and evaluation are Querini's reported claim, not an independently verified expenditure or assessment.",
            ["cand-2087", "cand-11983"], "Giacomo Querini, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-querini-1668-criticises-construction"),
        new_statement("st-chp6-p152-desolation-real-different-origins", "cand-4490", None,
            "haskell_says_much_querini_described_desolation_was_real_but_differently_caused",
            "Haskell says much of the desolation Querini described was real, although its origins were different.",
            (75, 75, "But, in fact, much of the desolation", "though its origins were very different."), False,
            "This is Haskell's assessment of Querini's description and its causes, not a relation between two represented entities.",
            ["cand-2087", "cand-4490"], "Haskell", "authorial historical assessment"),
        new_statement("st-chp6-p152-rosa-1664-no-commissions", "cand-2236", None,
            "rosa_says_he_had_received_no_commissions_for_a_year_in_1664",
            "In the 1664 quotation, Salvator Rosa says he had received no commissions for a full year.",
            (76, 76, "As for commissions", "for a full year,"), False,
            "The recipient and exact document are not identified; Rosa's statement is not independently checked against commission records.",
            ["cand-2236"], "Salvator Rosa, quoted by Haskell", "nested quotation from an unidentified written source",
            footnote_from="st-chp6-p152-rosa-1662-and-1664-letters"),
        new_statement("st-chp6-p152-rosa-1664-fears-worsening-war-news", "cand-2236", None,
            "rosa_says_worsening_war_news_might_make_him_give_up_painting",
            "Rosa says that if the war news worsened he might as well plant his brushes in the garden.",
            (76, 76, "and if the war news gets any worse", "in the garden"), False,
            "This is Rosa's conditional metaphor for abandoning painting, not a report that he stopped working.",
            ["cand-2236"], "Salvator Rosa, quoted by Haskell", "nested quotation from an unidentified written source",
            footnote_from="st-chp6-p152-rosa-1662-and-1664-letters",
            extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "source_line": 76,
                      "ocr": "6", "print": "5", "basis": "CHP-6.pdf physical page 7."}]}),
        new_statement("st-chp6-p152-alexander-repairs-roman-roads", "cand-0665", "cand-11985",
            "sagredo_reports_alexander_vii_attended_to_repairing_roman_roads",
            "Sagredo says Alexander VII had long paid particular attention to repairing Rome's roads.",
            (70, 70, "and repairing the roads", "and repairing the roads"), True,
            "This is the content of Sagredo's 1661 report as quoted by Haskell; no individual roads are named.",
            ["cand-2327", "cand-0665", "cand-11985"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation",
            relation_note="Sagredo explicitly attributes attention to road repair to Alexander VII."),
        new_statement("st-chp6-p152-alexander-surpasses-papal-predecessors", "cand-0665", "cand-11986",
            "sagredo_says_alexander_vii_surpassed_unnamed_predecessors_in_urban_work",
            "Sagredo says Alexander VII far surpassed his unnamed predecessors in this urban work.",
            (70, 70, "and truly in this labour", "his predecessors.. . ."), True,
            "The comparison is Sagredo's quoted assessment; the predecessors are unnamed and not individually enumerated.",
            ["cand-2327", "cand-0665", "cand-11986"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation",
            relation_note="Sagredo explicitly compares Alexander VII's urban work with that of his unnamed predecessors."),
        new_statement("st-chp6-p152-colonnades-encircle-piazza", "cand-6307", "cand-6308",
            "sagredo_reports_st_peters_colonnades_encircle_the_piazza",
            "Sagredo describes the colonnades as encircling the piazza di S. Pietro.",
            (70, 71, "The building", "piazza di S. Pietro"), True,
            "The quote is continued across the source line break; S0 inserts a leading apostrophe before 'of the colonnades' that is absent from the print.",
            ["cand-2327", "cand-6307", "cand-6308"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation",
            extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "source_line": 71,
                      "ocr": "' of the colonnades", "print": "of the colonnades", "basis": "CHP-6.pdf physical page 7."}]},
            relation_note="Sagredo explicitly states that the colonnades encircle the piazza."),
        new_statement("st-chp6-p152-colonnades-recall-ancient-rome", "cand-2327", None,
            "sagredo_calls_colonnades_an_achievement_recalling_ancient_rome",
            "Sagredo says the colonnades would be an achievement recalling the greatness of ancient Rome.",
            (71, 71, "will be an achievement", "ancient Rome."), False,
            "This is Sagredo's evaluative comparison, not an independent claim about the colonnades' historical significance.",
            ["cand-2327", "cand-6307", "cand-4490"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation"),
        new_statement("st-chp6-p152-colonnade-halfway-complete-estimate", "cand-6307", None,
            "sagredo_reports_colonnade_about_half_complete_with_three_years_remaining",
            "Sagredo reports an estimate that the colonnade work was about halfway complete and would take three more years.",
            (71, 71, "It is estimated that the work", "it will be complete."), False,
            "The estimate's speaker is unspecified in the quotation; it is not an independently verified schedule.",
            ["cand-2327", "cand-6307"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation"),
        new_statement("st-chp6-p152-sagredo-defers-advisability-judgment", "cand-2327", None,
            "sagredo_declines_to_judge_whether_urban_efforts_are_advisable",
            "Sagredo declines to judge whether such efforts were advisable at that moment and leaves the question to others.",
            (71, 71, "I am not going to discuss", "better than I do."), False,
            "This is Sagredo's stated restraint in the quotation, not an assessment of the policy's actual advisability.",
            ["cand-2327", "cand-6307"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation"),
        new_statement("st-chp6-p152-rome-buildings-population-observation", "cand-4490", None,
            "sagredo_observes_more_buildings_fewer_inhabitants_and_empty_houses_in_rome",
            "Sagredo observes that Rome had more buildings and fewer inhabitants, with empty houses and To Let signs in busy streets.",
            (71, 72, "It is true that Rome is getting", "To Let."), False,
            "These are Sagredo's observations and generalizations, not an independently verified building or population count.",
            ["cand-2327", "cand-4490", "cand-6320"], "Niccolò Sagredo, quoted by Haskell", "nested diplomatic quotation",
            footnote_from="st-chp6-p152-sagredo-1661-building-and-depopulation"),
    ]
    if len(new_statements) != len(NEW_STATEMENT_IDS) or {r["statement_id"] for r in new_statements} != set(NEW_STATEMENT_IDS):
        raise SystemExit("new statement set does not match the reviewed p.152 plan")

    # Retain the p.152 n.5 reference on the 1664 claims, not on Rosa's 1662 quotation.
    for row in new_statements:
        if row["statement_id"].startswith("st-chp6-p152-rosa-1664-"):
            row["qualifiers"].update(rosa_footnote)

    for row in new_statements:
        if row["statement_id"] in by_id:
            raise SystemExit(f"new p.152 statement ID already exists: {row['statement_id']}")
        by_id[row["statement_id"]] = row
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(new_statements)

    cov["note"] += (
        " p.152 physical page 7 was reviewed against CHP-6.pdf. The nine previously unset statements are classified and "
        "split into atomic claims where they combine distinct relations or source assessments. The Venetian ambassadors' "
        "poverty report and observation of Bernini's portico costs are separated; the p.151 financial-drains fragment is "
        "closed by the scalar resource claim here. Querini's quoted criticism is separated into attributed predictions, "
        "the architectural precinct relation, reported blame, causal malaria claim, and unverified expenditure. Sagredo's "
        "1661 report is separated into city beautification, road repair, comparison with predecessors, colonnade/piazza, "
        "progress estimate, evaluative judgment, and population observations. Rosa's 1662 and 1664 quotations are separated. "
        "Eight source-bounded candidates and eight mentions were added; the existing general-city mention was remapped to "
        "the abstract state term. OCR corrections are recorded in S2, with S0 preserved."
    )

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + candidates_to_add, cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(vfields, coverage, vbom),
    }
    final_rows = [by_id[sid] for sid in TARGETS] + new_statements
    summary = {
        "segment": SEGMENT, "previously_unset_classified": len(TARGETS),
        "new_atomic_statements": len(new_statements),
        "segment_statement_count_after": sum(row.get("segment_id") == SEGMENT for row in statements),
        "relation_candidates_in_segment_after": sum(row["qualifiers"].get("relation_candidate") is True for row in statements if row.get("segment_id") == SEGMENT),
        "non_relational_in_segment_after": sum(row["qualifiers"].get("relation_candidate") is False for row in statements if row.get("segment_id") == SEGMENT),
        "unset_in_segment_after": sum(row["qualifiers"].get("relation_candidate") is None for row in statements if row.get("segment_id") == SEGMENT),
        "candidates_added": CANDIDATE_IDS, "mentions_added": NEW_MENTION_IDS,
        "mention_remapped": "m-chp6-p152-179", "mode": "dry-run",
    }
    if summary["segment_statement_count_after"] != 31 or summary["unset_in_segment_after"] != 0:
        raise SystemExit(f"unexpected p.152 segment totals: {summary}")
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify and atomize p.152 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables, then atomically write reviewed results.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
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
