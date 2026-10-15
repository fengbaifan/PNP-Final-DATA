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
SEGMENT = "chp-6:06_CHP-6_sec_iv:l12-26"
BACKUP = ".bak-s2-chp6-seciv-p158-l12-26-semantics-20261013"

EXPECTED = {
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    STATEMENTS: "5d4139bb4d1ed6223075f398e464be237dd40d8fd73e58f9574f5c176603461b",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "1a4854217cd821631b52f976a88f81c2bcb983f7f886dfb16bcbc6bbf211266d",
    COVERAGE: "abb79aacb3d540f6922f8581521bf33ea02c82b88dc696714ae7762d58ebac1e",
}

TARGETS = {
    "st-chp6-p158-adami-1667-portrait-acquisitions",
    "st-chp6-p158-adami-collector-profile",
    "st-chp6-p158-adami-history-flower-quotation",
    "st-chp6-p158-adami-sought-portraits",
    "st-chp6-p158-angeloni-guardian",
    "st-chp6-p158-bellori-academy-member",
    "st-chp6-p158-bellori-antiquity-study",
    "st-chp6-p158-bellori-birth",
    "st-chp6-p158-bellori-catalogue",
    "st-chp6-p158-bellori-contemporary-interest",
    "st-chp6-p158-bellori-could-meet-domenichino",
    "st-chp6-p158-bellori-importance",
    "st-chp6-p158-bellori-lecture",
    "st-chp6-p158-bellori-lessons-from-domenichino",
    "st-chp6-p158-bellori-lives-partial",
    "st-chp6-p158-bellori-reported-kinship",
    "st-chp6-p158-bellori-saw-carracci-drawings",
    "st-chp6-p158-bellori-writing-development",
    "st-chp6-p158-collectors-interest-versus-painting-history",
    "st-chp6-p158-collectors-limited-influence",
    "st-chp6-p158-critic-rise-and-patron-decline",
    "st-chp6-p158-helmbrecker-admired",
    "st-chp6-p158-helmbrecker-pictures-for-marucelli",
    "st-chp6-p158-marucelli-arts-interest",
    "st-chp6-p158-marucelli-bambocciate",
    "st-chp6-p158-marucelli-books-passion",
    "st-chp6-p158-marucelli-commissioned-writer-busts",
    "st-chp6-p158-marucelli-information-to-baldinucci",
    "st-chp6-p158-marucelli-library",
    "st-chp6-p158-marucelli-library-record",
    "st-chp6-p158-marucelli-patronage-assessment",
    "st-chp6-p158-marucelli-patronage-refreshing",
    "st-chp6-p158-marucelli-residence",
    "st-chp6-p158-marucelli-wrote-lives",
    "st-chp6-p158-patron-to-critic-shift",
    "st-chp6-p158-writers-books-in-library",
}

TRUE_NOTES = {
    "st-chp6-p158-adami-1667-portrait-acquisitions": "Haskell reports Adami's 1667 writing about a recent acquisition. Retain the source mediation, unresolved sitter identities, and uncertainty about the writing's form.",
    "st-chp6-p158-adami-sought-portraits": "This records Adami's stated collecting aim; the index-defined portrait-collection candidate remains type-unresolved.",
    "st-chp6-p158-angeloni-guardian": "Haskell directly states Angeloni was Bellori's guardian; preserve the source attribution.",
    "st-chp6-p158-bellori-academy-member": "Haskell states Bellori became an active member of the Accademia at an early date; the institution candidate's identity mapping remains for S3.",
    "st-chp6-p158-bellori-catalogue": "This records Bellori's authorship of an unnamed catalogue of some leading Roman collections; title and scope remain unspecified.",
    "st-chp6-p158-bellori-could-meet-domenichino": "Preserve the source's modal 'could meet': it describes access or opportunity in Angeloni's house, not a documented meeting event.",
    "st-chp6-p158-bellori-importance": "Haskell ranks Bellori as the most important among the Roman critics whose influence began in the second half of the seventeenth century; this remains an attributed ranking.",
    "st-chp6-p158-bellori-lecture": "This records Bellori's 1664 lecture at the Accademia; the lecture's topic is split into a separate statement.",
    "st-chp6-p158-bellori-lessons-from-domenichino": "Haskell states Bellori took lessons from Domenichino; preserve the biographical source attribution.",
    "st-chp6-p158-bellori-lives-partial": "This is a source-grounded authorship candidate. The sentence continues at p. 159 and its existing continuation link is retained.",
    "st-chp6-p158-bellori-reported-kinship": "The nephew relationship is explicitly reported as hearsay ('was said to be'); keep it distinct from the direct guardian statement.",
    "st-chp6-p158-bellori-saw-carracci-drawings": "Haskell says Bellori could see this drawing group in Angeloni's house; retain the open identity match with cand-5932 for S3.",
    "st-chp6-p158-helmbrecker-admired": "This records Haskell's explicit account of Marucelli's admiration for Helmbrecker.",
    "st-chp6-p158-helmbrecker-pictures-for-marucelli": "Haskell reports sixteen pictures made for Marucelli; the work group and its unspecified individual titles remain distinct.",
    "st-chp6-p158-marucelli-bambocciate": "This records Marucelli's stated appreciation of Helmbrecker's bambocciate; keep the art category distinct from the Bamboccianti group.",
    "st-chp6-p158-marucelli-commissioned-writer-busts": "Haskell reports a commission for busts of great writers in several media. The writers and individual works are unnamed, so the object remains open.",
    "st-chp6-p158-marucelli-information-to-baldinucci": "This records Marucelli sending details about Rome-based artists to Baldinucci; the separate history-writing relation is recorded independently.",
    "st-chp6-p158-marucelli-library": "Haskell reports Marucelli amassed a considerable library; its type and identity remain unresolved.",
    "st-chp6-p158-marucelli-library-record": "This records the library in an unnamed scholarly work; do not equate it with Mare Magnum from footnote 1.",
    "st-chp6-p158-marucelli-residence": "Haskell completes the p. 157 introduction by locating Marucelli's residence at piazza di Spagna; no building is inferred.",
    "st-chp6-p158-marucelli-wrote-lives": "This records Marucelli's authorship of lives of principal painters; the additional friendship claim is separated.",
    "st-chp6-p158-writers-books-in-library": "Haskell says the writers' works filled Marucelli's library. The writers and books are an unnamed group, so the object remains open.",
}

FALSE_NOTES = {
    "st-chp6-p158-adami-collector-profile": "Descriptive introduction and authorial characterization; the portrait-seeking action is recorded separately.",
    "st-chp6-p158-adami-history-flower-quotation": "Attributed collecting maxim; it expresses Adami's view and does not assert a relation between identified entities.",
    "st-chp6-p158-bellori-antiquity-study": "Biographical activity without a specific entity endpoint.",
    "st-chp6-p158-bellori-birth": "Biographical date claim, not an entity relation; retain Haskell's approximate dating.",
    "st-chp6-p158-bellori-contemporary-interest": "General description of Bellori's intellectual attention, without a specific entity endpoint.",
    "st-chp6-p158-bellori-writing-development": "Career characterization and authorial contrast, without a specific entity relation.",
    "st-chp6-p158-collectors-interest-versus-painting-history": "Authorial assessment of the collectors' significance, not a specific relation.",
    "st-chp6-p158-collectors-limited-influence": "Authorial generalization about the collectors' influence; it is not an entity-to-entity claim.",
    "st-chp6-p158-critic-rise-and-patron-decline": "Qualified historical causal interpretation by Haskell, not a specific entity relation.",
    "st-chp6-p158-marucelli-arts-interest": "General characterization of Marucelli's interests; concrete actions are recorded separately.",
    "st-chp6-p158-marucelli-books-passion": "Authorial characterization of a personal interest, not a specific entity relation.",
    "st-chp6-p158-marucelli-patronage-assessment": "Haskell's interpretive assessment of taste and patronage, not a specific entity relation.",
    "st-chp6-p158-marucelli-patronage-refreshing": "Comparative evaluative judgment by Haskell, not a specific entity relation.",
    "st-chp6-p158-patron-to-critic-shift": "Broad historical interpretation of changing cultural influence, not a specific entity relation.",
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


def add_row(base, statement_id, subject, object_, predicate, claim, quote, start_line, end_line, mentioned, relation, copy_q_keys=()):
    row = {k: copy.deepcopy(base[k]) for k in ("segment_id", "origin", "source_file") if k in base}
    row.update({
        "statement_id": statement_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "original_quote": quote,
    })
    q = {}
    row["qualifiers"] = q
    base_q = base.get("qualifiers", {})
    for key in copy_q_keys:
        if key in base_q:
            q[key] = copy.deepcopy(base_q[key])
    q.update({
        "printed_page": "158",
        "pdf_physical_page": 13,
        "source_line_start": start_line,
        "source_line_end": end_line,
        "claim": claim,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
    })
    q.setdefault("speaker", "Haskell")
    q.setdefault("text_layer", "authorial historical account")
    if relation:
        q["relation_candidate_note"] = "Source-grounded S2 relation candidate; preserve Haskell's attribution and qualifications. No formal S6 edge is created."
    else:
        q["relation_candidate_note"] = "This is a general, descriptive, quoted, or evaluative claim rather than a specific entity relation candidate."
    if not object_ and relation:
        q["open_endpoint_reason"] = "The source describes a generic, unnamed group or work; it does not identify an individual endpoint. Preserve the claim without inventing a named entity."
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
        raise SystemExit(f"p.158 unset target set changed: {sorted(unset ^ TARGETS)}")

    _, candidates, _ = read_csv(CANDIDATES)
    candidate_ids = {r["candidate_id"] for r in candidates}
    required = {"cand-0014", "cand-0015", "cand-0166", "cand-0272", "cand-0892", "cand-1554", "cand-1555", "cand-1556", "cand-6413", "cand-6415", "cand-6416", "cand-6418", "cand-6419", "cand-6420", "cand-6423"}
    if not required <= candidate_ids:
        raise SystemExit(f"required candidate missing: {sorted(required - candidate_ids)}")

    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    for sid, note in FALSE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
    by_id["st-chp6-p158-marucelli-commissioned-writer-busts"]["qualifiers"]["open_endpoint_reason"] = (
        "The busts are described only as a group by material and generic sitters; no individual works or represented writers are named."
    )
    by_id["st-chp6-p158-writers-books-in-library"]["qualifiers"]["open_endpoint_reason"] = (
        "The great writers and the particular books that filled Marucelli's library are not named in this passage."
    )

    # Keep named sitters, group authorship, Baldinucci's history, and Bellori's lecture topic atomic.
    l13, l14, l15, l18, l19, l22, l23, l26 = (source_lines[i - 1] for i in (13, 14, 15, 18, 19, 22, 23, 26))
    quote_essex = l18[l18.index("he has just obtained pictures of Lord Essex"):l18.index(" and", l18.index("he has just obtained pictures of Lord Essex"))]
    quote_drach = l18[l18.index("pictures of Lord Essex and"):] + "\n" + l19[:l19.index(" among the English")]
    quote_friends = l13[l13.index("some of the principal painters"):l13.index(", and he sent details")]
    bald_start = l13.index("when that scholar was writing")
    quote_baldinucci = l13[bald_start:l13.index(".", bald_start) + 1]
    topic_start = l26.index("in 1664 he delivered a lecture")
    quote_topic = l26[topic_start:l26.index(" He was already", topic_start)]
    quote_critics = l22 + "\n" + l23[:l23.index(" was Gian Pietro Bellori.")]

    adami_base = by_id["st-chp6-p158-adami-1667-portrait-acquisitions"]
    footnote_keys = ("speaker", "text_layer", "qualification", "reported_author_candidate_id", "reported_date", "document_candidate_id", "cited_source_candidate_id", "footnote_markers", "footnote_source_lines", "footnote_segment_id", "footnote_link_status", "footnote_pending", "footnote_statement_ids", "footnote_refs")
    new_rows = [
        add_row(adami_base, "st-chp6-p158-adami-portrait-of-lord-essex", "cand-0015", "cand-6415", "collection_includes_portrait_of", "Haskell reports that Adami's portrait collection included a picture of Lord Essex.", quote_essex, 18, 18, ["cand-0015", "cand-6415"], True, footnote_keys),
        add_row(adami_base, "st-chp6-p158-adami-portrait-of-francesco-drach", "cand-0015", "cand-6416", "collection_includes_portrait_of", "Haskell reports that Adami's portrait collection included a picture of Francesco Drach.", quote_drach, 18, 19, ["cand-0015", "cand-6416"], True, footnote_keys),
        add_row(by_id["st-chp6-p158-marucelli-wrote-lives"], "st-chp6-p158-marucelli-friends-with-painters", "cand-1554", None, "befriended_many_painters", "Haskell says many of the principal painters whose lives Marucelli wrote were his friends.", quote_friends, 13, 13, ["cand-1554", "cand-1556"], True),
        add_row(by_id["st-chp6-p158-marucelli-information-to-baldinucci"], "st-chp6-p158-baldinucci-writing-history", "cand-0166", "cand-6413", "writing_history_of_italian_art", "Haskell says Baldinucci was writing his history of Italian art when Marucelli sent him information about artists working in Rome.", quote_baldinucci, 13, 13, ["cand-0166", "cand-6413"], True),
        add_row(by_id["st-chp6-p158-bellori-lecture"], "st-chp6-p158-bellori-lecture-topic", "cand-6419", "cand-6420", "lecture_concerned_ideal_in_art", "Haskell says Bellori's 1664 lecture to the Accademia concerned the Ideal in art.", quote_topic, 26, 26, ["cand-6419", "cand-6420"], True, ("date", "topic_candidate_id", "qualification", "footnote_markers", "footnote_source_lines", "footnote_segment_id", "footnote_link_status", "footnote_pending", "footnote_statement_ids", "footnote_refs")),
        add_row(by_id["st-chp6-p158-bellori-importance"], "st-chp6-p158-roman-critics-influence-began", "cand-0892", None, "influence_began_in_second_half_of_seventeenth_century", "Haskell says the influence of Roman critics began to be felt in the second half of the seventeenth century.", quote_critics, 22, 23, ["cand-0892"], False),
    ]
    for row in new_rows[:2]:
        row["qualifiers"]["qualification"] += " Candidate cand-0015 is an index-derived portrait-collection subentry whose type remains unresolved until S3; no individual picture is identified."
    new_rows[3]["qualifiers"]["claim"] = "Haskell says Baldinucci was writing his history of Italian art."

    # The indexed portrait collection is still a candidate, not an accepted KU; retain unresolved sitter identities.
    aq = by_id["st-chp6-p158-adami-1667-portrait-acquisitions"]["qualifiers"]
    existing_mentions = set(aq.get("mentioned_candidate_ids", []))
    aq["mentioned_candidate_ids"] = sorted(existing_mentions | {"cand-6415", "cand-6416"})
    aq["relation_candidate_note"] += " Lord Essex and Francesco Drach remain unresolved person candidates; their specific pictures are not individually identified. The portrait-collection index candidate remains type-unresolved for S3."

    # Split the sentence's Roman-critic framing from its ranking of Bellori.
    iq = by_id["st-chp6-p158-bellori-importance"]["qualifiers"]
    iq["claim"] = "Haskell ranks Gian Pietro Bellori as the most important among the Roman critics whose influence began in the second half of the seventeenth century."
    iq["mentioned_candidate_ids"] = ["cand-0272", "cand-0892"]
    by_id["st-chp6-p158-bellori-importance"]["predicate"] = "ranked_as_most_important_roman_critic"

    for row in new_rows:
        q = row["qualifiers"]
        if row["original_quote"] not in "\n".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]):
            raise SystemExit(f"new quote is not anchored: {row['statement_id']}")
        refs = set(q.get("mentioned_candidate_ids", [])) | {cid for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")) if cid}
        if refs - candidate_ids:
            raise SystemExit(f"new candidate reference missing: {row['statement_id']} -> {sorted(refs - candidate_ids)}")

    coverage_fields, coverage, coverage_bom = read_csv(COVERAGE)
    cov = next((r for r in coverage if r["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected coverage state: {cov}")
    cov["note"] = (
        "印本p.158正文L12–26逐条完成S2语义裁决：保留Marucelli、Adami与Bellori的具名关系、作品及文献候选；"
        "拆出Lord Essex与Francesco Drach肖像、Baldinucci著史、Bellori讲座主题及Marucelli画家友谊。"
        "Haskell的评价、引语、年代与历史解释按非关系陈述记录；未名画家、书籍与胸像组保持开放端点。"
        "跨页Lives句保留至p.159 L29的链接；印本校勘依据扫描只记S2，不改S0。"
    )

    output_rows = []
    for row in statements:
        output_rows.append(row)
        if row["statement_id"] == "st-chp6-p158-adami-1667-portrait-acquisitions":
            output_rows.extend(new_rows[:2])
        if row["statement_id"] == "st-chp6-p158-marucelli-wrote-lives":
            output_rows.append(new_rows[2])
        if row["statement_id"] == "st-chp6-p158-marucelli-information-to-baldinucci":
            output_rows.append(new_rows[3])
        if row["statement_id"] == "st-chp6-p158-bellori-lecture":
            output_rows.append(new_rows[4])
        if row["statement_id"] == "st-chp6-p158-bellori-importance":
            output_rows.append(new_rows[5])

    final_ids = [r["statement_id"] for r in output_rows]
    if len(final_ids) != len(set(final_ids)):
        raise SystemExit("duplicate statement ID after p.158 split")
    segment_rows = [r for r in output_rows if r.get("segment_id") == SEGMENT]
    true_count = sum(r["qualifiers"].get("relation_candidate") is True for r in segment_rows)
    false_count = sum(r["qualifiers"].get("relation_candidate") is False for r in segment_rows)
    unset_count = sum(r["qualifiers"].get("relation_candidate") is None for r in segment_rows)
    if (len(segment_rows), true_count, false_count, unset_count) != (42, 27, 15, 0):
        raise SystemExit(f"unexpected p.158 segment totals: {(len(segment_rows), true_count, false_count, unset_count)}")

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in output_rows) + "\n").encode("utf-8"),
        COVERAGE: csv_bytes(coverage_fields, coverage, coverage_bom),
    }
    summary = {
        "segment": SEGMENT,
        "classified_existing": len(TARGETS),
        "new_atomic_statements": len(new_rows),
        "relation_candidates_after": true_count,
        "non_relational_after": false_count,
        "unset_after": unset_count,
        "mode": "dry-run",
    }
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
