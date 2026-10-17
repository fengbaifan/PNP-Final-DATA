from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PROCESS_REF = "S3-procedure-type-review-2026-10-16"


NEW = {
    "cand-0897": (
        "sg3-procedure-customs-duty-pictures",
        "chp-8:08_CHP-8_sec_ii:l209-213#L211; chp-16:16_CHP-16_intro:l16-20#L18",
        "The index candidate links pp.228 and 374. Ch. 8 reports that sacred pictures paid lower customs duty than profane ones; ch. 16 describes customs difficulties in moving pictures. Treat these as the book's customs-duty practice concerning pictures, without inferring a particular statute, rate, or jurisdiction. No same-type procedure KU represents this identity.",
    ),
    "cand-11471": (
        "sg3-procedure-pieta-plan-selection",
        "chp-9:09_CHP-9_sec_ii:l70-78#L72",
        "The ch. 9 passage states that Pieta governors were required to seek plans from highly regarded painters with suitable ideas and choose the best. This is a source-defined selection procedure, distinct from the broader inspection of modelli and approval practices already represented in the manifest; retain Haskell's 'similar practice seems' qualification.",
    ),
    "cand-1514": (
        "sg3-procedure-manfrin-painter-competitions",
        "chp-17:17_CHP-17_sec_i:l22-25#L24; M.csv#51 p.381",
        "The index subentry under Girolamo Manfrin resolves at p.381: Manfrin organized competitions among painters to produce pictures on erotic themes he devised. This is a distinct painter-competition practice, not Manfrin's person KU or the existing noble banquet competition KU.",
    ),
    "cand-7498": (
        "sg3-procedure-florentine-flour-revenue-concession-1676",
        "chp-8:08_CHP-8_sec_i:l84-96#L85; chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4#L3",
        "The body calls this the lucrative nine-year flour monopoly awarded to Andrea del Rosso at age 36 and shared with Lorenzo; note 2 identifies the same concession as the Appalto Generale beginning 1 June 1676. Group the body and note candidates as one concession practice. Keep the decree/archive candidate separate from the concession itself.",
    ),
    "cand-9982": (
        "sg3-procedure-paintings-for-engraved-reproduction",
        "chp-13:13_CHP-13_intro:l14-19#L16",
        "Ch. 13 explicitly distinguishes this second production route—contemporary painters making pictures primarily for reproduction by an engraver—from reproducing established masterpieces, drawings made for book illustrations, and artists producing their own engravings. No existing procedure KU represents this route.",
    ),
    "cand-12414": (
        "sg3-procedure-florentine-flour-revenue-concession-1676",
        "chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4#L3",
        "Note 2 names the Appalto Generale concession of Florence flour revenues for nine years from 1 June 1676; the chapter body candidate cand-7498 describes this same grant as Andrea and Lorenzo del Rosso's flour monopoly. This row represents the concession, not the archival copy of its decree.",
    ),
}

SAME = {
    "cand-2423": (
        "units/terms/servitu-particolare",
        "chp-1:01_CHP-1_sec_ii:l4-14#L6; S.csv#111 pp.6-8",
        "The passage defines servitù particolare as the closest patron-artist employment relationship and describes its conditions. This is the historical term already represented by the existing term KU, not a procedure. Correct the candidate's suggested_type from procedure to term and reuse that KU; do not infer a specific service relationship between named people.",
    ),
}

PENDING = {
    "cand-11988": (
        "chp-6:06_CHP-6_sec_i:l69-76#L74",
        "The passage quotes Querini predicting that house demolition, increased fountain water, and extinguished fires would lead to malaria. It does not establish that these measures were proposed or implemented as a procedure. Keep undecided until the cited report and speaker context establish whether this is a procedure, a policy proposal, or only a reported prediction; do not create a KU meanwhile.",
    ),
    "cand-12252": (
        "chp-15:15_CHP-15_sec_ii:l90-113#L102",
        "The note reports an accusation that Querini obstructed plans to stop Brenta flooding because they threatened his garden, but identifies no plan, project, or authority; the cited secondary study pp.185-200 has not been independently consulted. Keep undecided pending an identified project and source sufficient to decide its procedure/event boundary.",
    ),
    "cand-1610": (
        "A.csv#129 pp.240-241",
        "The person-index subentry says Grand Prince Ferdinand was connected with art exhibitions, but it does not yet establish whether this candidate denotes a specific Florence exhibition/event, an organizing procedure, or the broader term. Review the cited pp.240-241 and the 1706 exhibition catalogue reference, then compare type and scope with the art-exhibition term candidates before grouping. Keep undecided; do not merge by shared wording.",
    ),
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_id(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def counts(alignments, candidates):
    decisions = decision_rows(alignments)
    by_type = Counter((candidates[row["candidate_id"]]["suggested_type"], row["decision"]) for row in decisions)
    all_decisions = Counter(row["decision"] for row in decisions)
    new_rows = [row for row in decisions if row["decision"] == "new"]
    groups = {group_id(row["resolution_note"]) for row in new_rows if group_id(row["resolution_note"])}
    return all_decisions, by_type, len(groups), len(new_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the prevalidated S3 alignment and candidate-type changes.")
    args = parser.parse_args()

    afields, alignments = read_csv(ALIGNMENT)
    cfields, candidate_rows = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    by_id = {row["candidate_id"]: row for row in decision_rows(alignments)}

    changed_ids = set(NEW) | set(SAME) | set(PENDING)
    assert len(changed_ids) == 10
    assert changed_ids <= set(by_id) and changed_ids <= set(candidates)
    assert {cid for cid, row in by_id.items() if candidates[cid]["suggested_type"] == "procedure" and row["decision"] == "undecided"} == changed_ids
    assert all(by_id[cid]["decision"] == "undecided" for cid in changed_ids)
    assert all(not by_id[cid]["ku_id"] for cid in NEW)
    assert candidates["cand-2423"]["suggested_type"] == "procedure"
    manifest_fields, manifest = read_csv(TABLES / "ku-manifest.csv")
    target = next((row for row in manifest if row["ku_id"] == SAME["cand-2423"][0]), None)
    assert target and target["type"] == "term"
    assert not any(group_id(by_id[cid]["resolution_note"]) == value[0] for cid, value in NEW.items())

    before_decisions, before_types, before_groups, before_new = counts(alignments, candidates)
    for cid, (new_group, source_ref, rationale) in NEW.items():
        row = by_id[cid]
        prior = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={new_group}; source_ref={source_ref}; S3 procedure type review 2026-10-16: undecided -> new. "
            f"{rationale} Prior rationale retained as history: {prior}"
        )

    for cid, (ku_id, source_ref, rationale) in SAME.items():
        row = by_id[cid]
        prior = row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = ku_id
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref={source_ref}; S3 procedure type review 2026-10-16: undecided -> same ({ku_id}); "
            f"{rationale} Prior rationale retained as history: {prior}"
        )
        candidates[cid]["suggested_type"] = "term"

    for cid, (source_ref, rationale) in PENDING.items():
        row = by_id[cid]
        prior = row["resolution_note"]
        group = group_id(prior) or f"sg3-procedure-{cid}"
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={group}; source_ref={source_ref}; S3 procedure type review 2026-10-16: undecided retained. "
            f"{rationale} Prior rationale retained as history: {prior}"
        )

    after_decisions, after_types, after_groups, after_new = counts(alignments, candidates)
    assert sum(after_decisions.values()) == sum(before_decisions.values())
    assert after_decisions["same"] == before_decisions["same"] + 1
    assert after_decisions["new"] == before_decisions["new"] + 6
    assert after_decisions["undecided"] == before_decisions["undecided"] - 7
    assert after_groups == before_groups + 5
    assert after_new == before_new + 6
    assert all(candidates[cid]["suggested_type"] == "term" for cid in SAME)
    assert all(by_id[cid]["decision"] == "undecided" for cid in PENDING)

    print("S3 procedure review dry-run passed")
    print("decision totals before:", dict(before_decisions))
    print("decision totals after:", dict(after_decisions))
    print("new groups/candidates before:", before_groups, before_new)
    print("new groups/candidates after:", after_groups, after_new)
    print("procedure decisions after:", {key[1]: value for key, value in after_types.items() if key[0] == "procedure"})
    print("term decisions after:", {key[1]: value for key, value in after_types.items() if key[0] == "term"})
    print("pending procedure IDs:", ", ".join(sorted(PENDING)))
    if args.apply:
        write_csv(ALIGNMENT, afields, alignments)
        write_csv(CANDIDATES, cfields, candidate_rows)
        print("applied: alignment decisions/routes and one suggested_type correction")
    else:
        print("dry-run only; pass --apply to write")


if __name__ == "__main__":
    main()
